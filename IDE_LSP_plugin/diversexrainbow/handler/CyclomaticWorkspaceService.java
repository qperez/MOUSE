package fr.irisa.diversexrainbow.handler;

import org.eclipse.lsp4j.DidChangeConfigurationParams;
import org.eclipse.lsp4j.DidChangeWatchedFilesParams;
import org.eclipse.lsp4j.services.WorkspaceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Handles workspace-level events.
 * Currently a minimal implementation - can be extended with workspace config.
 */
public class CyclomaticWorkspaceService implements WorkspaceService {

    private static final Logger LOG = LoggerFactory.getLogger(CyclomaticWorkspaceService.class);

    @Override
    public void didChangeConfiguration(DidChangeConfigurationParams params) {
        LOG.debug("Configuration changed: {}", params.getSettings());
        // Future: parse thresholds from settings
    }

    @Override
    public void didChangeWatchedFiles(DidChangeWatchedFilesParams params) {
        LOG.debug("Watched files changed: {} events", params.getChanges().size());
        // Future: handle external file changes
    }
}
