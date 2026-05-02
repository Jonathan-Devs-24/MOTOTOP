using CommunityToolkit.Mvvm.ComponentModel;

namespace MotoTop.Desktop.ViewModels;

public partial class SectionViewModel : ViewModelBase
{
    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private string _description = string.Empty;

    [ObservableProperty]
    private string _placeholder = string.Empty;

    public SectionViewModel(string title, string description, string placeholder)
    {
        Title = title;
        Description = description;
        Placeholder = placeholder;
    }
}
