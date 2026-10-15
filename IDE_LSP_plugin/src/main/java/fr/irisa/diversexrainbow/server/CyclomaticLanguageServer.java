package fr.irisa.diversexrainbow.server;

import fr.irisa.diversexrainbow.handler.CyclomaticTextDocumentService;
import fr.irisa.diversexrainbow.handler.CyclomaticWorkspaceService;
import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.services.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.CompletableFuture;

/**
 * Main Language Server implementation.
 * Handles initialization and capability negotiation with the LSP client (VSCode).
 */
public class CyclomaticLanguageServer implements LanguageServer, LanguageClientAware {

    private static final Logger LOG = LoggerFactory.getLogger(CyclomaticLanguageServer.class);

    private LanguageClient client;
    private final CyclomaticTextDocumentService textDocumentService;
    private final CyclomaticWorkspaceService workspaceService;
    private volatile FeedbackSettings feedbackSettings = FeedbackSettings.defaults();
    private int errorCode = 1;

    public CyclomaticLanguageServer() {
        this.textDocumentService = new CyclomaticTextDocumentService(this);
        this.workspaceService = new CyclomaticWorkspaceService(this::updateConfiguration);
    }

    @Override
    public CompletableFuture<InitializeResult> initialize(InitializeParams params) {
        LOG.info("Initializing LSP server, rootUri={}", params.getRootUri());
        updateFeedbackSettings(params.getInitializationOptions(), false);

        ServerCapabilities capabilities = new ServerCapabilities();

        // Register hover capability - this enables the "hover for complexity" feature
        capabilities.setHoverProvider(true);

        // Text document sync - we want full content on open/change
        TextDocumentSyncOptions syncOptions = new TextDocumentSyncOptions();
        syncOptions.setOpenClose(true);
        syncOptions.setChange(TextDocumentSyncKind.Full);
        capabilities.setTextDocumentSync(syncOptions);

        // Register diagnostics (optional: show warnings for high complexity methods)
        // Diagnostics are pushed, not pulled, so no capability needed here

        InitializeResult result = new InitializeResult(capabilities);

        ServerInfo serverInfo = new ServerInfo();
        serverInfo.setName("Cyclomatic Complexity LSP");
        serverInfo.setVersion("1.0.0");
        result.setServerInfo(serverInfo);

        LOG.info("LSP server initialized with hover and sync capabilities");
        return CompletableFuture.completedFuture(result);
    }

    @Override
    public CompletableFuture<Object> shutdown() {
        LOG.info("LSP server shutting down");
        errorCode = 0;
        return CompletableFuture.completedFuture(null);
    }

    @Override
    public void exit() {
        LOG.info("LSP server exiting with code {}", errorCode);
        System.exit(errorCode);
    }

    @Override
    public TextDocumentService getTextDocumentService() {
        return textDocumentService;
    }

    @Override
    public WorkspaceService getWorkspaceService() {
        return workspaceService;
    }

    @Override
    public void connect(LanguageClient client) {
        this.client = client;
        this.textDocumentService.setClient(client);
        LOG.info("LSP client connected");
    }

    @Override
    public void setTrace(SetTraceParams params) {
        // no-op: ignore trace notifications from client
    }

    public LanguageClient getClient() {
        return client;
    }

    public FeedbackSettings getFeedbackSettings() {
        return feedbackSettings;
    }

    private void updateConfiguration(Object settings) {
        updateFeedbackSettings(settings, true);
    }

    private void updateFeedbackSettings(Object settings, boolean refreshCurrentHover) {
        try {
            FeedbackSettings updatedSettings = FeedbackSettings.fromSettings(settings);
            feedbackSettings = updatedSettings;
            LOG.info("Applied feedback profile '{}'", updatedSettings.getActiveProfile());
            if (refreshCurrentHover) {
                textDocumentService.refreshFeedbackForCurrentHover();
            }
        } catch (IllegalArgumentException e) {
            LOG.error("Ignoring invalid cyclomaticLsp feedback settings: {}", e.getMessage());
        }
    }
}
