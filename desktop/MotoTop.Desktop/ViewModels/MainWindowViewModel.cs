using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using MotoTop.Desktop.Models;

namespace MotoTop.Desktop.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    public event EventHandler? LogoutRequested;

    [ObservableProperty]
    private ObservableCollection<MenuItemModel> _menuItems = new();

    [ObservableProperty]
    private MenuItemModel? _selectedMenuItem;

    [ObservableProperty]
    private ViewModelBase _selectedSectionViewModel = null!;

    public MainWindowViewModel()
    {
        MenuItems = new ObservableCollection<MenuItemModel>
        {
            new MenuItemModel("Inicio",
                "Resumen de la operación actual, pedidos y promociones",
                "Bienvenido a MotoTop! Selecciona una opción del menú para comenzar."),
            new MenuItemModel("Productos",
                "Gestiona el catálogo de repuestos y lista de precios",
                "Aquí podrás mantener actualizada la lista de productos y precios."),
            new MenuItemModel("Rubros",
                "Organiza los rubros de productos",
                "Crea, edita y elimina rubros para clasificar los productos."),
            new MenuItemModel("Proveedores",
                "Gestiona proveedores y su información",
                "Administra proveedores y condiciones de compra."),
            new MenuItemModel("Pedidos",
                "Controla los pedidos de vendedores",
                "Revisa pedidos pendientes, controles de stock y estado de envío."),
            new MenuItemModel("Clientes",
                "Visualiza clientes y saldos",
                "Consulta datos de clientes y su estado de cobranzas."),
            new MenuItemModel("Informes",
                "Genera reportes de ventas y cobranzas",
                "Consulta montos por vendedor, ventas totales y facturas pendientes de cobro.")
        };

        SelectedMenuItem = MenuItems[0];
    }

    partial void OnSelectedMenuItemChanged(MenuItemModel? value)
    {
        if (value is null)
        {
            SelectedSectionViewModel = new SectionViewModel("Sin sección",
                "Seleccione una opción del menú para comenzar.",
                "No hay contenido disponible.");
            return;
        }

        SelectedSectionViewModel = value.Title switch
        {
            "Productos" => new ProductManagementViewModel(),
            _ => new SectionViewModel(value.Title, value.Description, value.Placeholder)
        };
    }

    [RelayCommand]
    private void Logout()
    {
        LogoutRequested?.Invoke(this, EventArgs.Empty);
    }

    [RelayCommand]
    private void SelectMenuItem(MenuItemModel item)
    {
        if (item is null)
        {
            return;
        }

        SelectedMenuItem = item;
    }
}
