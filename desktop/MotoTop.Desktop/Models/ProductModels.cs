namespace MotoTop.Desktop.Models;

public class RubroModel
{
    public string Nombre { get; set; } = string.Empty;

    public override string ToString() => Nombre;
}

public class ProveedorModel
{
    public string Nombre { get; set; } = string.Empty;
    public string Telefono { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;

    public override string ToString() => Nombre;
}

public class PromocionModel
{
    public string Nombre { get; set; } = string.Empty;
    public string Tipo { get; set; } = string.Empty;
    public string FechaInicio { get; set; } = string.Empty;
    public string FechaFin { get; set; } = string.Empty;

    public override string ToString() => Nombre;
}

public class ProductModel
{
    public string Nombre { get; set; } = string.Empty;
    public decimal PrecioBase { get; set; }
    public int Stock { get; set; }
    public RubroModel? Rubro { get; set; }
    public ProveedorModel? Proveedor { get; set; }
    public PromocionModel? Promocion { get; set; }

    public override string ToString() => Nombre;
}
