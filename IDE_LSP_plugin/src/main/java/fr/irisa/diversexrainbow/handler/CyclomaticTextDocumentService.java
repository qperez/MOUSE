package fr.irisa.diversexrainbow.handler;

import fr.irisa.diversexrainbow.analyzer.CyclomaticComplexityAnalyzer;
import fr.irisa.diversexrainbow.analyzer.MethodComplexity;
import fr.irisa.diversexrainbow.server.CyclomaticLanguageServer;
import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.jsonrpc.messages.Either;
import org.eclipse.lsp4j.services.LanguageClient;
import org.eclipse.lsp4j.services.TextDocumentService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.ObjectNode;

import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.concurrent.CompletableFuture;

import static java.net.http.HttpClient.newHttpClient;
import static java.net.http.HttpRequest.newBuilder;

public class CyclomaticTextDocumentService implements TextDocumentService {

    private static final Logger LOG = LoggerFactory.getLogger(CyclomaticTextDocumentService.class);
    private static final String WEBHOOK_URL = "http://localhost:5000/metric/complexity";
    private final HttpClient httpClient = newHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();

    private final CyclomaticLanguageServer server;
    private final CyclomaticComplexityAnalyzer analyzer;
    private LanguageClient client;

    private final Map<String, String> documents = new HashMap<>();

    private MethodComplexity currentHoveredMethod = null;

    public CyclomaticTextDocumentService(CyclomaticLanguageServer server) {
        this.server = server;
        this.analyzer = new CyclomaticComplexityAnalyzer();
    }

    public void setClient(LanguageClient client) {
        this.client = client;
    }

    @Override
    public void didOpen(DidOpenTextDocumentParams params) {
        String uri = params.getTextDocument().getUri();
        String content = params.getTextDocument().getText();
        LOG.info("didOpen: {}", uri);
        if (isJavaFile(uri)) {
            documents.put(uri, content);
            analyzeAndPublishDiagnostics(uri, content);
        }
    }

    @Override
    public void didChange(DidChangeTextDocumentParams params) {
        String uri = params.getTextDocument().getUri();
        LOG.debug("didChange: {}", uri);
        if (!isJavaFile(uri)) return;

        List<TextDocumentContentChangeEvent> changes = params.getContentChanges();
        if (changes == null || changes.isEmpty()) return;

        String content = changes.get(changes.size() - 1).getText();
        documents.put(uri, content);
        analyzeAndPublishDiagnostics(uri, content);
    }

    @Override
    public void didClose(DidCloseTextDocumentParams params) {
        String uri = params.getTextDocument().getUri();
        LOG.info("didClose: {}", uri);
        documents.remove(uri);
        analyzer.invalidate(uri);

        // Leave forcé à la fermeture du fichier
        if (currentHoveredMethod != null) {
            sendLeaveEvent(uri, currentHoveredMethod);
            currentHoveredMethod = null;
        }

        if (client != null) {
            PublishDiagnosticsParams clearParams = new PublishDiagnosticsParams(uri, Collections.emptyList());
            client.publishDiagnostics(clearParams);
        }
    }

    @Override
    public void didSave(DidSaveTextDocumentParams params) {
        String uri = params.getTextDocument().getUri();
        LOG.debug("didSave: {}", uri);
        String content = documents.get(uri);
        if (content != null && isJavaFile(uri)) {
            analyzeAndPublishDiagnostics(uri, content);
        }
    }

    @Override
    public CompletableFuture<Hover> hover(HoverParams params) {
        String uri = params.getTextDocument().getUri();
        int line = params.getPosition().getLine() + 1;

        if (!isJavaFile(uri)) return CompletableFuture.completedFuture(null);

        List<MethodComplexity> methods = analyzer.getCached(uri);
        if (methods.isEmpty()) {
            String content = documents.get(uri);
            if (content == null) return CompletableFuture.completedFuture(null);
            try {
                methods = analyzer.analyze(uri, content);
            } catch (Exception e) {
                return CompletableFuture.completedFuture(null);
            }
        }

        // ── Méthode sous le curseur (startLine <= line <= endLine) ─────────
        MethodComplexity current = null;
        for (MethodComplexity mc : methods) {
            if (mc.getStartLine() <= line && line <= mc.getEndLine()) {
                current = mc;
                break;
            }
        }

        // ── Enter / Leave ──────────────────────────────────────────────────────
        if (current != null && !current.equals(currentHoveredMethod)) {
            // On change de méthode → leave l'ancienne
            /*if (currentHoveredMethod != null) {
                sendLeaveEvent(uri, currentHoveredMethod);
            }*/
            sendEnterEvent(uri, current);
            currentHoveredMethod = current;
        } else if (current == null && currentHoveredMethod != null) {
            // On est sur du texte mais hors méthode (imports, champs, etc.)
            MethodComplexity emptyMethodComplexity = new MethodComplexity("","","",0,0,0);
            sendLeaveEvent(uri, emptyMethodComplexity);
            currentHoveredMethod = null;
        }

        if (current == null) return CompletableFuture.completedFuture(null);

        MarkupContent markupContent = new MarkupContent();
        markupContent.setKind(MarkupKind.MARKDOWN);
        markupContent.setValue(current.toHoverMarkdown());

        return CompletableFuture.completedFuture(new Hover(markupContent,
                new Range(new Position(current.getStartLine() - 1, 0),
                        new Position(current.getStartLine() - 1, Integer.MAX_VALUE))));
    }

    private void sendEnterEvent(String uri, MethodComplexity mc) {
        sendEvent("enter", uri, mc);
    }

    private void sendLeaveEvent(String uri, MethodComplexity mc) {
        sendEvent("leave", uri, mc);
    }

    private void sendEvent(String event, String uri, MethodComplexity mc) {
        CompletableFuture.runAsync(() -> {
            try {
                ObjectNode node = objectMapper.createObjectNode();
                node.put("event", event);
                node.put("uri", uri);
                node.put("className", mc.getClassName());
                node.put("methodName", mc.getMethodName());
                node.put("signature", mc.getSignature());
                node.put("complexity", mc.getComplexity());
                node.put("startLine", mc.getStartLine());
                node.put("endLine", mc.getEndLine());

                HttpRequest request = newBuilder()
                        .uri(java.net.URI.create(WEBHOOK_URL))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(node)))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                LOG.debug("Event '{}' sent → HTTP {}", event, response.statusCode());
            } catch (Exception e) {
                LOG.warn("Failed to send '{}' event: {}", event, e.getMessage());
            }
        });
    }

    private void analyzeAndPublishDiagnostics(String uri, String content) {
        CompletableFuture.runAsync(() -> {
            List<MethodComplexity> methods = analyzer.analyze(uri, content);
            if (client == null) return;

            List<Diagnostic> diagnostics = new ArrayList<>();
            for (MethodComplexity mc : methods) {
                if (mc.getComplexity() > CyclomaticComplexityAnalyzer.MEDIUM_THRESHOLD) {
                    diagnostics.add(buildDiagnostic(mc));
                }
            }

            client.publishDiagnostics(new PublishDiagnosticsParams(uri, diagnostics));
            LOG.debug("Published {} diagnostics for {}", diagnostics.size(), uri);
        });
    }

    private Diagnostic buildDiagnostic(MethodComplexity mc) {
        Range range = new Range(
                new Position(mc.getStartLine() - 1, 0),
                new Position(mc.getStartLine() - 1, Integer.MAX_VALUE)
        );

        DiagnosticSeverity severity;
        String message;

        if (mc.getComplexity() > CyclomaticComplexityAnalyzer.HIGH_THRESHOLD) {
            severity = DiagnosticSeverity.Error;
            message = String.format("☠️ Very high cyclomatic complexity: %d (method: %s). Refactor immediately!",
                    mc.getComplexity(), mc.getSignature());
        } else {
            severity = DiagnosticSeverity.Warning;
            message = String.format("🔴 High cyclomatic complexity: %d (method: %s). Consider refactoring.",
                    mc.getComplexity(), mc.getSignature());
        }

        Diagnostic diag = new Diagnostic(range, message);
        diag.setSeverity(severity);
        diag.setSource("cyclomatic-lsp");
        diag.setCode(Either.forLeft("CC" + mc.getComplexity()));
        return diag;
    }

    private boolean isJavaFile(String uri) {
        return uri != null && uri.endsWith(".java");
    }
}