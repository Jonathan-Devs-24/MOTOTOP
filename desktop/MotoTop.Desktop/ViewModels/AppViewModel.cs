using CommunityToolkit.Mvvm.ComponentModel;
using System;
using MotoTop.Desktop.Services;
using MotoTop.Desktop.ViewModels;

namespace MotoTop.Desktop.ViewModels;

public partial class AppViewModel : ViewModelBase
{
    private readonly AuthService _authService;

    [ObservableProperty]
    private ViewModelBase _currentViewModel = null!;

    public AppViewModel(AuthService authService)
    {
        _authService = authService;
        SetLoginView();
    }

    private void SetLoginView()
    {
        var loginViewModel = new LoginViewModel(_authService);
        loginViewModel.LoginSuccess += OnLoginSuccess;
        CurrentViewModel = loginViewModel;
    }

    private void OnLoginSuccess(object? sender, EventArgs e)
    {
        var mainViewModel = new MainWindowViewModel();
        mainViewModel.LogoutRequested += OnLogoutRequested;
        CurrentViewModel = mainViewModel;
    }

    private void OnLogoutRequested(object? sender, EventArgs e)
    {
        SetLoginView();
    }
}