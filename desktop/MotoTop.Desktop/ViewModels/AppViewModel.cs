using CommunityToolkit.Mvvm.ComponentModel;
using System;
using MotoTop.Desktop.Services;
using MotoTop.Desktop.ViewModels;

namespace MotoTop.Desktop.ViewModels;

public partial class AppViewModel : ViewModelBase
{
    private readonly AuthService _authService;

    [ObservableProperty]
    private ViewModelBase _currentViewModel;

    public AppViewModel(AuthService authService)
    {
        _authService = authService;
        var loginViewModel = new LoginViewModel(_authService);
        loginViewModel.LoginSuccess += OnLoginSuccess;
        CurrentViewModel = loginViewModel;
    }

    private void OnLoginSuccess(object? sender, EventArgs e)
    {
        // Cambiar a la vista principal
        CurrentViewModel = new MainWindowViewModel();
    }
}