package fr.irisa.diversexrainbow.analyzer;

/**
 * Represents the cyclomatic complexity result for a single method or constructor.
 */
public class MethodComplexity {

    private final String className;
    private final String methodName;
    private final String signature;
    private final int startLine;   // 1-based line number
    private final int endLine;     // 1-based line number
    private final int complexity;

    public MethodComplexity(String className, String methodName, String signature,
                            int startLine, int endLine, int complexity) {
        this.className = className;
        this.methodName = methodName;
        this.signature = signature;
        this.startLine = startLine;
        this.endLine = endLine;
        this.complexity = complexity;
    }

    public String getClassName() {
        return className;
    }

    public String getMethodName() {
        return methodName;
    }

    public String getSignature() {
        return signature;
    }

    public int getStartLine() {
        return startLine;
    }

    public int getEndLine() {
        return endLine;
    }

    public int getComplexity() {
        return complexity;
    }

    /**
     * Returns the Markdown content for the LSP hover tooltip.
     */
    public String toHoverMarkdown() {
        return String.format(
                "### Cyclomatic Complexity\n\n" +
                "|                |       |\n" +
                "|----------------|-------|\n" +
                "| **Method**     | `%s` |\n" +
                "| **Complexity** | **%d** |\n" +
                "%s\n\n",
                signature,
                complexity,
                getComplexityExplanation()
        );
    }

    private String getComplexityExplanation() {
        if (complexity <= CyclomaticComplexityAnalyzer.LOW_THRESHOLD) {
            return "> 💚 Low complexity — easy to test and maintain.";
        } else if (complexity <= CyclomaticComplexityAnalyzer.MEDIUM_THRESHOLD) {
            return "> 🟡 Moderate complexity — consider simplifying if possible.";
        } else if (complexity <= CyclomaticComplexityAnalyzer.HIGH_THRESHOLD) {
            return "> 🔴 High complexity — difficult to test, refactoring recommended.";
        } else {
            return "> ☠️ Very high complexity — extremely difficult to test and maintain. Refactor now!";
        }
    }

    @Override
    public String toString() {
        return String.format("MethodComplexity{name='%s', lines=%d-%d, complexity=%d}",
                methodName, startLine, endLine, complexity);
    }
}
