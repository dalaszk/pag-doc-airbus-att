// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Handle navigation clicks
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Handle "Postuler" button clicks
    const postulerButtons = document.querySelectorAll('.btn-primary');
    postulerButtons.forEach(button => {
        if (button.textContent.includes('Postuler')) {
            button.addEventListener('click', function() {
                const candidatureSection = document.querySelector('#candidature');
                if (candidatureSection) {
                    candidatureSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        }
    });

    // File upload handling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const wrapper = this.closest('.file-input-wrapper');
            const display = wrapper.querySelector('.file-input-display span');
            
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                display.textContent = fileName;
                wrapper.classList.add('has-file');
            } else {
                display.textContent = 'Cliquez pour sélectionner un fichier';
                wrapper.classList.remove('has-file');
            }
        });
    });

    // Form submission handling
    const candidatureForm = document.getElementById('candidatureForm');
    if (candidatureForm) {
        candidatureForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitButton = this.querySelector('.btn-submit');
            const originalText = submitButton.textContent;
            
            // Show loading state
            submitButton.textContent = 'Envoi en cours...';
            submitButton.disabled = true;
            
            try {
                const formData = new FormData(this);
                
                const response = await fetch('/api/candidature', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showNotification('Candidature envoyée avec succès!', 'success');
                    this.reset();
                    
                    // Reset file upload displays
                    const fileWrappers = this.querySelectorAll('.file-input-wrapper');
                    fileWrappers.forEach(wrapper => {
                        wrapper.classList.remove('has-file');
                        const display = wrapper.querySelector('.file-input-display span');
                        display.textContent = 'Cliquez pour sélectionner un fichier';
                    });
                } else {
                    const error = await response.json();
                    showNotification(error.message || 'Erreur lors de l\'envoi de la candidature', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Erreur de connexion. Veuillez réessayer.', 'error');
            } finally {
                // Reset button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }

    // Form validation
    const requiredInputs = document.querySelectorAll('input[required], textarea[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
});

// Field validation function
function validateField(field) {
    const value = field.value.trim();
    const isValid = field.checkValidity() && value !== '';
    
    if (isValid) {
        field.classList.remove('error');
        field.classList.add('valid');
    } else {
        field.classList.remove('valid');
        field.classList.add('error');
    }
    
    return isValid;
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
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
        
        .notification-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }
        
        .notification-close:hover {
            opacity: 0.8;
        }
    `;
    
    if (!document.querySelector('#notification-styles')) {
        style.id = 'notification-styles';
        document.head.appendChild(style);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Handle close button
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        removeNotification(notification);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            removeNotification(notification);
        }
    }, 5000);
}

function removeNotification(notification) {
    notification.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 300);
}

// Scroll animations
function handleScrollAnimations() {
    const animatedElements = document.querySelectorAll('.job-card, .benefit-card, .stat-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(element);
    });
}

// Initialize scroll animations when page loads
document.addEventListener('DOMContentLoaded', handleScrollAnimations);

// Header scroll effect
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.backdropFilter = 'blur(10px)';
    } else {
        header.style.background = '#ffffff';
        header.style.backdropFilter = 'none';
    }
});

// File size validation
function validateFileSize(file, maxSizeMB = 10) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
}

// File type validation
function validateFileType(file, allowedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']) {
    const fileName = file.name.toLowerCase();
    return allowedTypes.some(type => fileName.endsWith(type.toLowerCase()));
}

// Enhanced file input handling with validation
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const wrapper = this.closest('.file-input-wrapper');
            const display = wrapper.querySelector('.file-input-display span');
            
            if (file) {
                // Validate file size
                if (!validateFileSize(file)) {
                    showNotification('Le fichier est trop volumineux. Taille maximale: 10MB', 'error');
                    this.value = '';
                    return;
                }
                
                // Validate file type
                if (!validateFileType(file)) {
                    showNotification('Type de fichier non autorisé. Formats acceptés: PDF, DOC, DOCX, JPG, PNG', 'error');
                    this.value = '';
                    return;
                }
                
                display.textContent = file.name;
                wrapper.classList.add('has-file');
            } else {
                display.textContent = 'Cliquez pour sélectionner un fichier';
                wrapper.classList.remove('has-file');
            }
        });
    });
});

