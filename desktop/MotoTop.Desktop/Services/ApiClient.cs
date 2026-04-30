// desktop/MotoTop.Desktop/Services/ApiClient.cs
using System;
using System.Net.Http;
using System.Net.Http.Headers;

public class ApiClient
{
    private readonly HttpClient _http;

    public ApiClient(AuthService authService)
    {
        var baseUrl = Environment.GetEnvironmentVariable("MOTOTOP_API_URL")
                      ?? "http://localhost:8000/";

        _http = new HttpClient
        {
            BaseAddress = new Uri(baseUrl)
        };

        if (!string.IsNullOrEmpty(authService.AccessToken))
        {
            _http.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", authService.AccessToken);
        }
    }

    public HttpClient Http => _http;
}