using System.Collections.Generic;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

public class ProductoService
{
    private readonly HttpClient _http;
    private readonly JsonSerializerOptions _options;

    public ProductoService(ApiClient apiClient)
    {
        _http = apiClient.Http;

        _options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
    }

    public async Task<List<ProductoDto>?> GetProductos()
    {
        var response = await _http.GetAsync("api/productos/");

        if (!response.IsSuccessStatusCode)
            return null;

        var json = await response.Content.ReadAsStringAsync();

        return JsonSerializer.Deserialize<List<ProductoDto>>(json, _options);
    }
}