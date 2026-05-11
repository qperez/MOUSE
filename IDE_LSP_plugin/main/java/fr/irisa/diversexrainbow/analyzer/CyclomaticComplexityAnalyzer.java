package fr.irisa.diversexrainbow.analyzer;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.CallableDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.nodeTypes.NodeWithSimpleName;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.*;

public class CyclomaticComplexityAnalyzer {

    /**
     * Return a human-readable risk label based on McCabe's thresholds.
     * 1-5:   Simple, low risk
     * 6-10:  Moderate complexity
     * 11-20: High complexity, consider refactoring
     * 20+:   Very high, untestable
     */
    public static final int LOW_THRESHOLD    = 5;
    public static final int MEDIUM_THRESHOLD = 10;
    public static final int HIGH_THRESHOLD   = 20;

    private final Map<String, List<MethodComplexity>> cache = new HashMap<>();
    public String lastError = null;

    public List<MethodComplexity> analyze(String uri, String content) {
        try {
            List<MethodComplexity> results = parseAndAnalyze(content);
            cache.put(uri, results);
            lastError = null;
            return results;
        } catch (Exception e) {
            lastError = e.getClass().getSimpleName() + ": " + e.getMessage();
            return Collections.emptyList();
        }
    }

    public List<MethodComplexity> getCached(String uri) {
        return cache.getOrDefault(uri, Collections.emptyList());
    }

    public void invalidate(String uri) {
        cache.remove(uri);
    }

    public Optional<MethodComplexity> findMethodAtLine(String uri, int line) {
        return getCached(uri).stream()
                .filter(m -> line >= m.getStartLine() && line <= m.getEndLine())
                .findFirst();
    }

    private List<MethodComplexity> parseAndAnalyze(String content) {
        ParserConfiguration config = new ParserConfiguration();
        config.setLanguageLevel(ParserConfiguration.LanguageLevel.JAVA_21);
        JavaParser parser = new JavaParser(config);

        ParseResult<CompilationUnit> result = parser.parse(content);
        if (!result.isSuccessful() || result.getResult().isEmpty()) {
            // Tenter un parse plus permissif si erreur
            throw new RuntimeException("Parse failed: " +
                    result.getProblems().stream()
                            .map(Object::toString)
                            .reduce("", (a, b) -> a + "; " + b));
        }

        CompilationUnit cu = result.getResult().get();
        List<MethodComplexity> results = new ArrayList<>();

        // Méthodes
        cu.findAll(MethodDeclaration.class).forEach(method -> {
            int startLine = method.getBegin().map(p -> p.line).orElse(0);
            int endLine   = method.getEnd().map(p -> p.line).orElse(startLine);
            int complexity = computeComplexity(method);
            String sig     = method.getNameAsString() + method.getParameters().toString()
                    .replace("[", "(").replace("]", ")");

            String className = method.findAncestor(ClassOrInterfaceDeclaration.class)
                    .map(NodeWithSimpleName::getNameAsString)
                    .orElse("Unknown");

            results.add(new MethodComplexity(className,method.getNameAsString(), sig, startLine, endLine, complexity));
        });

        // Constructeurs
        cu.findAll(ConstructorDeclaration.class).forEach(ctor -> {
            int startLine  = ctor.getBegin().map(p -> p.line).orElse(0);
            int endLine    = ctor.getEnd().map(p -> p.line).orElse(startLine);
            int complexity = computeComplexity(ctor);
            String sig     = ctor.getNameAsString() + ctor.getParameters().toString()
                    .replace("[", "(").replace("]", ")");

            String className = ctor.findAncestor(com.github.javaparser.ast.body.ClassOrInterfaceDeclaration.class)
                    .map(NodeWithSimpleName::getNameAsString)
                    .orElse("Unknown");

            results.add(new MethodComplexity(className,ctor.getNameAsString(), sig, startLine, endLine, complexity));
        });

        results.sort(Comparator.comparingInt(MethodComplexity::getStartLine));
        return results;
    }

    private int computeComplexity(CallableDeclaration<?> callable) {
        CyclomaticVisitor visitor = new CyclomaticVisitor();
        callable.accept(visitor, null);
        return visitor.complexity;
    }

    /**
     * Visiteur AST qui compte les points de décision.
     * Complexité = 1 + nombre de branches.
     */
    private static class CyclomaticVisitor extends VoidVisitorAdapter<Void> {
        int complexity = 1;

        @Override public void visit(IfStmt n, Void arg)          { complexity++; super.visit(n, arg); }
        @Override public void visit(ForStmt n, Void arg)         { complexity++; super.visit(n, arg); }
        @Override public void visit(ForEachStmt n, Void arg)     { complexity++; super.visit(n, arg); }
        @Override public void visit(WhileStmt n, Void arg)       { complexity++; super.visit(n, arg); }
        @Override public void visit(DoStmt n, Void arg)          { complexity++; super.visit(n, arg); }
        @Override public void visit(CatchClause n, Void arg)     { complexity++; super.visit(n, arg); }
        @Override public void visit(SwitchEntry n, Void arg)     { complexity++; super.visit(n, arg); }
        @Override public void visit(ConditionalExpr n, Void arg) { complexity++; super.visit(n, arg); }

        @Override
        public void visit(BinaryExpr n, Void arg) {
            if (n.getOperator() == BinaryExpr.Operator.AND ||
                    n.getOperator() == BinaryExpr.Operator.OR) {
                complexity++;
            }
            super.visit(n, arg);
        }
    }
}