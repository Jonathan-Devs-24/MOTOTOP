using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Threading.Tasks;
using MotoTop.Desktop.Models;
using MotoTop.Desktop.Services;

namespace MotoTop.Desktop.ViewModels;

public partial class LoginViewModel : ViewModelBase
{
    private readonly AuthService _authService;

    public event EventHandler? LoginSuccess;

    [ObservableProperty]
    private string _username = string.Empty;

    [ObservableProperty]
    private string _password = string.Empty;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _isLoading = false;

    public LoginViewModel(AuthService authService)
    {
        _authService = authService;
    }

    [RelayCommand]
    private async Task LoginAsync()
    {
        IsLoading = true;
        ErrorMessage = string.Empty;

        var request = new LoginRequest
        {
            Username = Username,
            Password = Password
        };

        var (response, errorMessage) = await _authService.LoginAsync(request);

        if (response != null)
        {
            LoginSuccess?.Invoke(this, EventArgs.Empty);
        }
        else
        {
            ErrorMessage = string.IsNullOrWhiteSpace(errorMessage)
                ? "Credenciales inválidas"
                : errorMessage;
        }

        IsLoading = false;
    }
}