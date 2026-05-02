namespace MotoTop.Desktop.Models;

public class MenuItemModel
{
    public string Title { get; set; }
    public string Description { get; set; }
    public string Placeholder { get; set; }

    public MenuItemModel(string title, string description, string placeholder)
    {
        Title = title;
        Description = description;
        Placeholder = placeholder;
    }
}
