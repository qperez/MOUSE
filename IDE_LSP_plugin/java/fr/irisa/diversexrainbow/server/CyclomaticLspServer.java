package fr.irisa.diversexrainbow.server;

import org.eclipse.lsp4j.jsonrpc.Launcher;
import org.eclipse.lsp4j.launch.LSPLauncher;
import org.eclipse.lsp4j.services.LanguageClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.concurrent.Future;

/**
 * Entry point for the Cyclomatic Complexity LSP Server.
 * Communicates via stdin/stdout with the VSCode extension.
 */
public class CyclomaticLspServer {

    private static final Logger LOG = LoggerFactory.getLogger(CyclomaticLspServer.class);

    public static void main(String[] args) throws Exception {
        LOG.info("Starting Cyclomatic Complexity LSP Server...");

        InputStream in = System.in;
        OutputStream out = System.out;

        CyclomaticLanguageServer server = new CyclomaticLanguageServer();

        Launcher<LanguageClient> launcher = LSPLauncher.createServerLauncher(server, in, out);

        LanguageClient client = launcher.getRemoteProxy();
        server.connect(client);

        LOG.info("LSP Server connected, listening for requests...");

        Future<?> listening = launcher.startListening();
        listening.get(); // Block until connection closes
    }
}
