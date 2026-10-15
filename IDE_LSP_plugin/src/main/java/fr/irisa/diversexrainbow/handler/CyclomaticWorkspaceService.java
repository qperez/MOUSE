package fr.irisa.diversexrainbow.handler;

import org.eclipse.lsp4j.DidChangeConfigurationParams;
import org.eclipse.lsp4j.DidChangeWatchedFilesParams;
import org.eclipse.lsp4j.services.WorkspaceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

/**
 * Handles workspace-level events.
 */
public class CyclomaticWorkspaceService implements WorkspaceService {

    private static final Logger LOG = LoggerFactory.getLogger(CyclomaticWorkspaceService.class);
    private final Consumer<Object> configurationHandler;

    public CyclomaticWorkspaceService(Consumer<Object> configurationHandler) {
        this.configurationHandler = configurationHandler;
    }

    @Override
    public void didChangeConfiguration(DidChangeConfigurationParams params) {
        LOG.info("Configuration changed: {}", params.getSettings());
        configurationHandler.accept(params.getSettings());
    }

    @Override
    public void didChangeWatchedFiles(DidChangeWatchedFilesParams params) {
        LOG.info("Watched files changed: {} events", params.getChanges().size());
        // Future: handle external file changes
    }
}
