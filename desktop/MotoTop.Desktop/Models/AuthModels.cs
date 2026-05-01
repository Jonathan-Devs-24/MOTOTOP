namespace MotoTop.Desktop.Models;

using System.Text.Json.Serialization;

public class LoginRequest
{
    [JsonPropertyName("username")]
    public string Username { get; set; } = string.Empty;

    [JsonPropertyName("password")]
    public string Password { get; set; } = string.Empty;
}

public class LoginResponse
{
    [JsonPropertyName("access")]
    public string Access { get; set; } = string.Empty;

    [JsonPropertyName("refresh")]
    public string Refresh { get; set; } = string.Empty;
}