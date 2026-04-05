<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}برج المراقبة{% endblock %}</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --sidebar-width: 260px;
            --sidebar-collapsed-width: 80px;
            --p-color: #1a0033;
            --gold: #FFD700;
        }

        body {
            font-family: 'Cairo', sans-serif;
            background: #0b0b0b;
            color: white;
            margin: 0;
            display: flex;
        }

        /* القائمة الجانبية الذكية */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--p-color);
            height: 100vh;
            position: fixed;
            right: 0;
            top: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1050;
            border-left: 1px solid rgba(255, 215, 0, 0.1);
            overflow: hidden;
        }

        .nav-link {
            display: flex;
            align-items: center;
            padding: 15px 25px;
            color: rgba(255, 255, 255, 0.6);
            text-decoration: none;
            margin: 5px 10px;
            border-radius: 12px;
            white-space: nowrap; /* منع النص من النزول لسطر جديد */
        }

        .nav-link i {
            min-width: 30px;
            font-size: 20px;
            text-align: center;
            margin-left: 15px;
        }

        .nav-link span {
            transition: opacity 0.3s;
        }

        /* --- استجابة الشاشات المتوسطة (التابلت) --- */
        @media (max-width: 1200px) and (min-width: 992px) {
            .sidebar { width: var(--sidebar-collapsed-width); }
            .sidebar .nav-link span, .sidebar h5 { display: none; }
            .sidebar .logo-img { width: 40px; }
            .main-wrapper { margin-right: var(--sidebar-collapsed-width) !important; }
            .nav-link { justify-content: center; padding: 15px; }
            .nav-link i { margin-left: 0; }
        }

        /* --- استجابة الشاشات الصغيرة (الجوال) --- */
        @media (max-width: 991px) {
            .sidebar { right: -280px; } /* تختفي تماماً */
            .sidebar.active { right: 0; width: var(--sidebar-width); }
            .sidebar.active .nav-link span { display: inline; }
            .main-wrapper { margin-right: 0 !important; }
            .mobile-btn { display: block !important; }
        }

        .main-wrapper {
            margin-right: var(--sidebar-width);
            flex: 1;
            transition: all 0.3s ease;
        }

        .top-bar {
            height: 70px;
            background: #121212;
            display: flex;
            align-items: center;
            padding: 0 20px;
            border-bottom: 1px solid #222;
        }

        .nav-link.active, .nav-link:hover {
            background: rgba(255, 215, 0, 0.1);
            color: var(--gold);
        }
    </style>
</head>
<body>

    <aside class="sidebar" id="sidebar">
        <div class="p-4 text-center border-bottom border-secondary mb-3">
            <img src="https://cdn.qumra.cloud/media/67f7f6d5f0b82f44a47bf845/1770229315912-117966978.webp" class="logo-img" width="70" style="filter: brightness(0) invert(1);">
            <h5 class="mt-2 text-gold" style="font-size: 12px; color: var(--gold);">برج المراقبة</h5>
        </div>
        
        <nav>
            <a href="{{ url_for('admin_dashboard') }}" class="nav-link {% if request.endpoint == 'admin_dashboard' %}active{% endif %}">
                <i class="fas fa-chart-pie"></i> <span>الإحصائيات</span>
            </a>
            <a href="{{ url_for('vendors_accreditation') }}" class="nav-link {% if request.endpoint == 'vendors_accreditation' %}active{% endif %}">
                <i class="fas fa-users-shield"></i> <span>الموردين</span>
            </a>
            <a href="#" class="nav-link">
                <i class="fas fa-vault"></i> <span>الرقابة المالية</span>
            </a>
            <a href="{{ url_for('logout') }}" class="nav-link text-danger mt-4">
                <i class="fas fa-power-off"></i> <span>خروج</span>
            </a>
        </nav>
    </aside>

    <div class="main-wrapper">
        <header class="top-bar">
            <button class="btn text-white mobile-btn d-none" onclick="document.getElementById('sidebar').classList.toggle('active')">
                <i class="fas fa-bars fa-lg"></i>
            </button>
            
            <div class="ms-3 fw-bold text-gold">محجوب أونلاين <span class="text-white small ms-2 d-none d-sm-inline">● النظام المركزي</span></div>
            
            <div class="ms-auto d-flex align-items-center bg-dark px-3 py-1 rounded-pill border border-secondary">
                <small class="me-2 d-none d-md-inline">{{ session['username'] if session['username'] else 'علي محجوب' }}</small>
                <i class="fas fa-crown text-gold"></i>
            </div>
        </header>

        <main class="p-4">
            {% block content %}{% endblock %}
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
