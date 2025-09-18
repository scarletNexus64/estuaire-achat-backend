/* =============================================
   🚀 ESTUAIRE E-COMMERCE DASHBOARD JAVASCRIPT
   ============================================= */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // =============================================
    // 🎨 DASHBOARD INITIALIZATION
    // =============================================
    initializeEstuaireDashboard();

    function initializeEstuaireDashboard() {
        console.log('🎯 ESTUAIRE Dashboard Loading...');
        
        // Initialize all dashboard components
        initializeAnimations();
        initializeInteractiveElements();
        initializeTooltips();
        initializeCharts();
        initializeRealTimeUpdates();
        
        console.log('✅ ESTUAIRE Dashboard Loaded Successfully!');
    }

    // =============================================
    // ✨ SMOOTH ANIMATIONS & TRANSITIONS
    // =============================================
    function initializeAnimations() {
        // Animate info boxes on load
        const infoBoxes = document.querySelectorAll('.info-box');
        infoBoxes.forEach((box, index) => {
            box.style.opacity = '0';
            box.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                box.style.transition = 'all 0.6s ease';
                box.style.opacity = '1';
                box.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Animate tables
        const tables = document.querySelectorAll('.table tbody tr');
        tables.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                row.style.transition = 'all 0.4s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 50);
        });
    }

    // =============================================
    // 🎯 INTERACTIVE ELEMENTS
    // =============================================
    function initializeInteractiveElements() {
        // Enhanced hover effects for cards
        const cards = document.querySelectorAll('.card, .info-box');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
                this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
            });
        });

        // Enhanced button interactions
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Ripple effect
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.6);
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // =============================================
    // 💡 ENHANCED TOOLTIPS
    // =============================================
    function initializeTooltips() {
        // Add custom tooltips to elements
        const tooltipElements = document.querySelectorAll('[data-toggle="tooltip"]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
        });

        function showTooltip(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'estuaire-tooltip';
            tooltip.textContent = this.getAttribute('title') || this.getAttribute('data-original-title');
            tooltip.style.cssText = `
                position: absolute;
                background: #1F2937;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            
            setTimeout(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(0)';
            }, 10);
            
            this.tooltipElement = tooltip;
        }

        function hideTooltip() {
            if (this.tooltipElement) {
                this.tooltipElement.style.opacity = '0';
                this.tooltipElement.style.transform = 'translateY(10px)';
                setTimeout(() => {
                    if (this.tooltipElement) {
                        this.tooltipElement.remove();
                        this.tooltipElement = null;
                    }
                }, 300);
            }
        }
    }

    // =============================================
    // 📊 DASHBOARD CHARTS & ANALYTICS
    // =============================================
    function initializeCharts() {
        // Sales Chart (if Chart.js is available)
        if (typeof Chart !== 'undefined') {
            initializeSalesChart();
            initializeProductChart();
        }
    }

    function initializeSalesChart() {
        const ctx = document.getElementById('salesChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
                datasets: [{
                    label: 'Ventes (FCFA)',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#6366F1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' FCFA';
                            }
                        }
                    }
                }
            }
        });
    }

    function initializeProductChart() {
        const ctx = document.getElementById('productChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Actifs', 'En Attente', 'Vendus', 'Inactifs'],
                datasets: [{
                    data: [45, 12, 28, 15],
                    backgroundColor: [
                        '#10B981',
                        '#F59E0B',
                        '#EF4444',
                        '#6B7280'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // =============================================
    // 🔄 REAL-TIME UPDATES
    // =============================================
    function initializeRealTimeUpdates() {
        // Update dashboard stats every 30 seconds
        setInterval(updateDashboardStats, 30000);
        
        // Add notification system
        initializeNotifications();
    }

    function updateDashboardStats() {
        const statElements = document.querySelectorAll('.info-box-number');
        statElements.forEach(element => {
            // Add a subtle glow effect when updating
            element.style.textShadow = '0 0 10px rgba(99, 102, 241, 0.5)';
            setTimeout(() => {
                element.style.textShadow = 'none';
            }, 1000);
        });
    }

    function initializeNotifications() {
        // Create notification container
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'estuaire-notifications';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 350px;
        `;
        document.body.appendChild(notificationContainer);

        // Example notification (you can trigger this from your Django views)
        window.showEstuaireNotification = function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} estuaire-notification`;
            notification.style.cssText = `
                margin-bottom: 10px;
                border-radius: 8px;
                border: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideInRight 0.3s ease;
                position: relative;
                overflow: hidden;
            `;
            
            notification.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <i class="fas fa-${getNotificationIcon(type)} mr-2"></i>
                    ${message}
                    <button type="button" class="close ml-auto" style="border: none; background: none;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            notificationContainer.appendChild(notification);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
            
            // Manual close
            notification.querySelector('.close').addEventListener('click', () => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            });
        };

        function getNotificationIcon(type) {
            const icons = {
                'success': 'check-circle',
                'info': 'info-circle',
                'warning': 'exclamation-triangle',
                'danger': 'times-circle'
            };
            return icons[type] || 'info-circle';
        }
    }

    // =============================================
    // 🎨 CSS ANIMATIONS (Injected via JS)
    // =============================================
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .estuaire-notification {
            animation: slideInRight 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    // =============================================
    // 🔧 UTILITY FUNCTIONS
    // =============================================
    
    // Format numbers for display
    window.formatNumber = function(num) {
        return new Intl.NumberFormat('fr-FR').format(num);
    };
    
    // Format currency
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'XOF'
        }).format(amount);
    };
    
    // Smooth scroll to element
    window.scrollToElement = function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    };

    console.log('🎯 ESTUAIRE Dashboard JavaScript Initialized');
});