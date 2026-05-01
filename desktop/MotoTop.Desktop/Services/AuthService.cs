using System.Net.Http.Json;
using System.Net.Http;
using System.Threading.Tasks;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using MotoTop.Desktop.Models;

namespace MotoTop.Desktop.Services;

public class AuthService
{
    private readonly HttpClient _httpClient;

    public string? AccessToken { get; private set; }
    public string? RefreshToken { get; private set; }

    public AuthService()
    {
        _httpClient = new HttpClient
        {
            BaseAddress = new Uri("http://localhost:8000") // Asumiendo que el backend corre en localhost:8000
        };
    }

    public async Task<(LoginResponse? Response, string? ErrorMessage)> LoginAsync(LoginRequest request)
    {
        try
        {
            var json = JsonSerializer.Serialize(request, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
            });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync("/api/token/", content);
            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return (null, responseBody);
            }

            var result = JsonSerializer.Deserialize<LoginResponse>(responseBody, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });
            if (result != null)
            {
                AccessToken = result.Access;
                RefreshToken = result.Refresh;
            }
            return (result, null);
        }
        catch (HttpRequestException ex)
        {
            return (null, ex.Message);
        }
        catch (Exception ex)
        {
            return (null, ex.Message);
        }
    }

    public async Task<string?> RefreshTokenAsync(string refreshToken)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync("/api/token/refresh/", new { refresh = refreshToken });
            response.EnsureSuccessStatusCode();
            var result = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
            return result?["access"];
        }
        catch
        {
            return null;
        }
    }
}