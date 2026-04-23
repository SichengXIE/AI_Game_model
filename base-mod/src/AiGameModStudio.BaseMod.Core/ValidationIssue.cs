namespace AiGameModStudio.BaseMod.Core;

public enum ValidationSeverity
{
    Warning,
    Error
}

public sealed record ValidationIssue(
    ValidationSeverity Severity,
    string Code,
    string Message,
    string Path);

public sealed class ValidationReport
{
    public List<ValidationIssue> Issues { get; } = [];

    public bool HasErrors => Issues.Any(issue => issue.Severity == ValidationSeverity.Error);

    public void Error(string code, string message, string path)
    {
        Issues.Add(new ValidationIssue(ValidationSeverity.Error, code, message, path));
    }

    public void Warning(string code, string message, string path)
    {
        Issues.Add(new ValidationIssue(ValidationSeverity.Warning, code, message, path));
    }
}
