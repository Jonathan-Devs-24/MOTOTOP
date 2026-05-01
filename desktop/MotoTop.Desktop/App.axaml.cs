using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Data.Core;
using Avalonia.Data.Core.Plugins;
using System.Linq;
using Avalonia.Markup.Xaml;
using MotoTop.Desktop.ViewModels;
using MotoTop.Desktop.Views;
using MotoTop.Desktop.Services;

namespace MotoTop.Desktop;

public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            var authService = new AuthService();
            desktop.MainWindow = new MainWindow
            {
                DataContext = new AppViewModel(authService),
            };
        }

        base.OnFrameworkInitializationCompleted();
    }
}