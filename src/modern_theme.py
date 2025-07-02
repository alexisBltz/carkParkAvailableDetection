"""
Tema moderno y oscuro para CarPark GUI
Estilos y configuraciones visuales avanzadas
"""
import tkinter as tk
from tkinter import ttk

class ModernDarkTheme:
    """Tema oscuro moderno para la aplicación"""
    
    # Paleta de colores moderna
    COLORS = {
        # Colores principales
        'bg_primary': '#1e1e1e',      # Fondo principal muy oscuro
        'bg_secondary': '#2d2d2d',    # Fondo secundario
        'bg_tertiary': '#3c3c3c',     # Fondo terciario
        'bg_card': '#252525',         # Fondo de tarjetas
        
        # Colores de acento
        'accent_blue': '#0078d4',     # Azul principal
        'accent_green': '#16c60c',    # Verde éxito
        'accent_orange': '#ff8c00',   # Naranja advertencia
        'accent_red': '#d83b01',      # Rojo error
        'accent_purple': '#8b5cf6',   # Púrpura moderno
        
        # Colores de texto
        'text_primary': '#ffffff',    # Texto principal
        'text_secondary': '#b0b0b0',  # Texto secundario
        'text_muted': '#808080',      # Texto tenue
        
        # Colores de borde
        'border_light': '#404040',    # Borde claro
        'border_medium': '#555555',   # Borde medio
        'border_dark': '#2a2a2a',     # Borde oscuro
        
        # Estados
        'hover': '#404040',           # Hover
        'active': '#4a4a4a',          # Activo
        'selected': '#0078d4',        # Seleccionado
        'disabled': '#666666',        # Deshabilitado
    }
    
    @classmethod
    def configure_styles(cls, root: tk.Tk):
        """Configura los estilos del tema oscuro"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Configurar colores generales
        style.configure('.',
                       background=cls.COLORS['bg_primary'],
                       foreground=cls.COLORS['text_primary'],
                       bordercolor=cls.COLORS['border_medium'],
                       darkcolor=cls.COLORS['bg_secondary'],
                       lightcolor=cls.COLORS['bg_tertiary'],
                       troughcolor=cls.COLORS['bg_secondary'],
                       selectbackground=cls.COLORS['selected'],
                       selectforeground=cls.COLORS['text_primary'],
                       fieldbackground=cls.COLORS['bg_tertiary'],
                       font=('Segoe UI', 9))
        
        # Configurar Frame
        style.configure('TFrame',
                       background=cls.COLORS['bg_primary'],
                       borderwidth=0)
        
        style.configure('Card.TFrame',
                       background=cls.COLORS['bg_card'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=cls.COLORS['border_light'])
        
        # Configurar LabelFrame
        style.configure('TLabelframe',
                       background=cls.COLORS['bg_primary'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=2,
                       bordercolor=cls.COLORS['border_medium'])
        
        style.configure('TLabelframe.Label',
                       background=cls.COLORS['bg_primary'],
                       foreground=cls.COLORS['accent_blue'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configurar Button
        style.configure('TButton',
                       background=cls.COLORS['bg_tertiary'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=1,
                       bordercolor=cls.COLORS['border_medium'],
                       focuscolor='none',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('TButton',
                 background=[('active', cls.COLORS['hover']),
                            ('pressed', cls.COLORS['active'])])
        
        # Botones de acción
        style.configure('Action.TButton',
                       background=cls.COLORS['accent_blue'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=0,
                       font=('Segoe UI', 9, 'bold'))
        
        style.map('Action.TButton',
                 background=[('active', '#106ebe'),
                            ('pressed', '#005a9e')])
        
        # Botones de éxito
        style.configure('Success.TButton',
                       background=cls.COLORS['accent_green'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=0)
        
        style.map('Success.TButton',
                 background=[('active', '#14b00c'),
                            ('pressed', '#12a00a')])
        
        # Botones de advertencia
        style.configure('Warning.TButton',
                       background=cls.COLORS['accent_orange'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=0)
        
        # Botones de error
        style.configure('Danger.TButton',
                       background=cls.COLORS['accent_red'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=0)
        
        # Configurar Label
        style.configure('TLabel',
                       background=cls.COLORS['bg_primary'],
                       foreground=cls.COLORS['text_primary'],
                       font=('Segoe UI', 9))
        
        style.configure('Title.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground=cls.COLORS['accent_blue'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=cls.COLORS['text_secondary'])
        
        style.configure('Info.TLabel',
                       foreground=cls.COLORS['text_muted'],
                       font=('Segoe UI', 8))
        
        # Configurar Entry
        style.configure('TEntry',
                       fieldbackground=cls.COLORS['bg_tertiary'],
                       foreground=cls.COLORS['text_primary'],
                       bordercolor=cls.COLORS['border_medium'],
                       insertcolor=cls.COLORS['text_primary'])
        
        # Configurar Combobox
        style.configure('TCombobox',
                       fieldbackground=cls.COLORS['bg_tertiary'],
                       foreground=cls.COLORS['text_primary'],
                       bordercolor=cls.COLORS['border_medium'],
                       selectbackground=cls.COLORS['selected'])
        
        # Configurar Scrollbar
        style.configure('TScrollbar',
                       background=cls.COLORS['bg_tertiary'],
                       bordercolor=cls.COLORS['border_medium'],
                       arrowcolor=cls.COLORS['text_secondary'],
                       troughcolor=cls.COLORS['bg_secondary'])
        
        # Configurar Progressbar
        style.configure('TProgressbar',
                       background=cls.COLORS['accent_blue'],
                       troughcolor=cls.COLORS['bg_secondary'],
                       borderwidth=0,
                       lightcolor=cls.COLORS['accent_blue'],
                       darkcolor=cls.COLORS['accent_blue'])
        
        # Configurar Notebook (pestañas)
        style.configure('TNotebook',
                       background=cls.COLORS['bg_primary'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_secondary'],
                       padding=(12, 8),
                       borderwidth=0)
        
        style.map('TNotebook.Tab',
                 background=[('selected', cls.COLORS['bg_tertiary']),
                            ('active', cls.COLORS['hover'])],
                 foreground=[('selected', cls.COLORS['text_primary']),
                            ('active', cls.COLORS['text_primary'])])
        
        # Configurar Treeview
        style.configure('Treeview',
                       background=cls.COLORS['bg_tertiary'],
                       foreground=cls.COLORS['text_primary'],
                       fieldbackground=cls.COLORS['bg_tertiary'],
                       borderwidth=0)
        
        style.configure('Treeview.Heading',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=1,
                       bordercolor=cls.COLORS['border_medium'])
        
        # Configurar root window
        root.configure(bg=cls.COLORS['bg_primary'])
        
        return style

class ModernWidgets:
    """Widgets personalizados con estilo moderno"""
    
    @staticmethod
    def create_title_bar(parent, title: str, subtitle: str = ""):
        """Crea una barra de título moderna"""
        title_frame = ttk.Frame(parent, style='Card.TFrame')
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Título principal
        title_label = ttk.Label(title_frame, text=title, style='Title.TLabel')
        title_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # Subtítulo
        if subtitle:
            subtitle_label = ttk.Label(title_frame, text=subtitle, style='Info.TLabel')
            subtitle_label.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        return title_frame
    
    @staticmethod
    def create_info_card(parent, title: str, content: str = "", icon: str = "ℹ️"):
        """Crea una tarjeta de información"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Header con icono
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        icon_label = ttk.Label(header_frame, text=icon, font=('Segoe UI', 12))
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(header_frame, text=title, style='Subtitle.TLabel')
        title_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Contenido
        if content:
            content_label = ttk.Label(card_frame, text=content, wraplength=250)
            content_label.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        return card_frame
    
    @staticmethod
    def create_action_button(parent, text: str, command, style: str = "Action.TButton", icon: str = ""):
        """Crea un botón de acción moderno"""
        button_text = f"{icon} {text}" if icon else text
        button = ttk.Button(parent, text=button_text, command=command, style=style)
        return button
    
    @staticmethod
    def create_status_indicator(parent, status: str, color: str = "green"):
        """Crea un indicador de estado"""
        status_frame = ttk.Frame(parent)
        
        # Círculo indicador
        canvas = tk.Canvas(status_frame, width=12, height=12, 
                          bg=ModernDarkTheme.COLORS['bg_primary'], 
                          highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        color_map = {
            'green': ModernDarkTheme.COLORS['accent_green'],
            'red': ModernDarkTheme.COLORS['accent_red'],
            'orange': ModernDarkTheme.COLORS['accent_orange'],
            'blue': ModernDarkTheme.COLORS['accent_blue']
        }
        
        canvas.create_oval(2, 2, 10, 10, fill=color_map.get(color, color), outline="")
        
        # Texto del estado
        status_label = ttk.Label(status_frame, text=status)
        status_label.pack(side=tk.LEFT)
        
        return status_frame

class ModernTooltip:
    """Tooltips modernos para la interfaz"""
    
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """Muestra el tooltip"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg=ModernDarkTheme.COLORS['bg_secondary'])
        
        label = tk.Label(tw, text=self.text,
                        background=ModernDarkTheme.COLORS['bg_secondary'],
                        foreground=ModernDarkTheme.COLORS['text_primary'],
                        relief=tk.SOLID,
                        borderwidth=1,
                        font=('Segoe UI', 9),
                        padx=8, pady=4)
        label.pack()
    
    def on_leave(self, event=None):
        """Oculta el tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
