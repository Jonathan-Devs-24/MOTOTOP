// MotoTop.Desktop/Services/AuthService.cs
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class AuthService
{
    private readonly HttpClient _http;
    private readonly JsonSerializerOptions _jsonOptions;

    public string? AccessToken { get; private set; }
    public string? RefreshToken { get; private set; }

    public AuthService()
    {
        var baseUrl = Environment.GetEnvironmentVariable("MOTOTOP_API_URL")
                      ?? "http://localhost:8000/";

        _http = new HttpClient
        {
            BaseAddress = new Uri(baseUrl)
        };

        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
    }

    public async Task<bool> Login(string username, string password)
    {
        var request = new LoginRequest
        {
            username = username,
            password = password
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _http.PostAsync("api/token/", content);

        if (!response.IsSuccessStatusCode)
            return false;

        var responseJson = await response.Content.ReadAsStringAsync();

        var result = JsonSerializer.Deserialize<LoginResponse>(
            responseJson,
            _jsonOptions
        );

        AccessToken = result?.access;
        RefreshToken = result?.refresh;

        return AccessToken != null;
    }

    public void AttachToken(HttpClient client)
    {
        if (AccessToken == null)
            return;

        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", AccessToken);
    }
}