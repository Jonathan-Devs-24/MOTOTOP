using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using MotoTop.Desktop.Models;

namespace MotoTop.Desktop.ViewModels;

public partial class ProductManagementViewModel : ViewModelBase
{
    [ObservableProperty]
    private ObservableCollection<RubroModel> _rubros = new();

    [ObservableProperty]
    private ObservableCollection<ProveedorModel> _proveedores = new();

    [ObservableProperty]
    private ObservableCollection<PromocionModel> _promociones = new();

    [ObservableProperty]
    private ObservableCollection<ProductModel> _productos = new();

    [ObservableProperty]
    private string _newRubroNombre = string.Empty;

    [ObservableProperty]
    private string _newProveedorNombre = string.Empty;

    [ObservableProperty]
    private string _newProveedorTelefono = string.Empty;

    [ObservableProperty]
    private string _newProveedorEmail = string.Empty;

    [ObservableProperty]
    private string _newPromocionNombre = string.Empty;

    [ObservableProperty]
    private string _newPromocionTipo = string.Empty;

    [ObservableProperty]
    private string _newPromocionInicio = string.Empty;

    [ObservableProperty]
    private string _newPromocionFin = string.Empty;

    [ObservableProperty]
    private string _newProductoNombre = string.Empty;

    [ObservableProperty]
    private decimal _newProductoPrecioBase = 0m;

    [ObservableProperty]
    private int _newProductoStock = 0;

    [ObservableProperty]
    private RubroModel? _selectedRubroForProducto;

    [ObservableProperty]
    private ProveedorModel? _selectedProveedorForProducto;

    [ObservableProperty]
    private PromocionModel? _selectedPromocionForProducto;

    public ProductManagementViewModel()
    {
        // Datos de ejemplo iniciales
        Rubros.Add(new RubroModel { Nombre = "Motor" });
        Rubros.Add(new RubroModel { Nombre = "Frenos" });

        Proveedores.Add(new ProveedorModel { Nombre = "Repuestos Goya", Telefono = "03777-123456", Email = "ventas@repuestosgoya.com" });
        Proveedores.Add(new ProveedorModel { Nombre = "MotoParts", Telefono = "03777-789012", Email = "contacto@motoparts.com" });

        Promociones.Add(new PromocionModel { Nombre = "Promo verano", Tipo = "Descuento", FechaInicio = "2026-05-01", FechaFin = "2026-05-31" });

        SelectedRubroForProducto = Rubros.Count > 0 ? Rubros[0] : null;
        SelectedProveedorForProducto = Proveedores.Count > 0 ? Proveedores[0] : null;
        SelectedPromocionForProducto = null;
    }

    [RelayCommand]
    private void AddRubro()
    {
        if (string.IsNullOrWhiteSpace(NewRubroNombre))
        {
            return;
        }

        var nuevo = new RubroModel { Nombre = NewRubroNombre.Trim() };
        Rubros.Add(nuevo);
        NewRubroNombre = string.Empty;

        if (SelectedRubroForProducto == null)
        {
            SelectedRubroForProducto = nuevo;
        }
    }

    [RelayCommand]
    private void AddProveedor()
    {
        if (string.IsNullOrWhiteSpace(NewProveedorNombre) || string.IsNullOrWhiteSpace(NewProveedorTelefono) || string.IsNullOrWhiteSpace(NewProveedorEmail))
        {
            return;
        }

        var nuevo = new ProveedorModel
        {
            Nombre = NewProveedorNombre.Trim(),
            Telefono = NewProveedorTelefono.Trim(),
            Email = NewProveedorEmail.Trim()
        };

        Proveedores.Add(nuevo);
        NewProveedorNombre = string.Empty;
        NewProveedorTelefono = string.Empty;
        NewProveedorEmail = string.Empty;

        if (SelectedProveedorForProducto == null)
        {
            SelectedProveedorForProducto = nuevo;
        }
    }

    [RelayCommand]
    private void AddPromocion()
    {
        if (string.IsNullOrWhiteSpace(NewPromocionNombre) || string.IsNullOrWhiteSpace(NewPromocionTipo) || string.IsNullOrWhiteSpace(NewPromocionInicio) || string.IsNullOrWhiteSpace(NewPromocionFin))
        {
            return;
        }

        var nueva = new PromocionModel
        {
            Nombre = NewPromocionNombre.Trim(),
            Tipo = NewPromocionTipo.Trim(),
            FechaInicio = NewPromocionInicio.Trim(),
            FechaFin = NewPromocionFin.Trim()
        };

        Promociones.Add(nueva);
        NewPromocionNombre = string.Empty;
        NewPromocionTipo = string.Empty;
        NewPromocionInicio = string.Empty;
        NewPromocionFin = string.Empty;

        if (SelectedPromocionForProducto == null)
        {
            SelectedPromocionForProducto = nueva;
        }
    }

    [RelayCommand]
    private void AddProducto()
    {
        if (string.IsNullOrWhiteSpace(NewProductoNombre) || NewProductoPrecioBase <= 0 || NewProductoStock < 0)
        {
            return;
        }

        var nuevo = new ProductModel
        {
            Nombre = NewProductoNombre.Trim(),
            PrecioBase = NewProductoPrecioBase,
            Stock = NewProductoStock,
            Rubro = SelectedRubroForProducto,
            Proveedor = SelectedProveedorForProducto,
            Promocion = SelectedPromocionForProducto
        };

        Productos.Add(nuevo);
        NewProductoNombre = string.Empty;
        NewProductoPrecioBase = 0m;
        NewProductoStock = 0;
        SelectedPromocionForProducto = null;
    }
}
