// Chat Widget JavaScript
class ChatWidget {
    constructor() {
        this.modal = null;
        this.currentTab = 'webchat';
        this.init();
    }

    init() {
        this.createButton();
        this.createModal();
        this.attachEventListeners();
    }

    createButton() {
        const button = document.createElement('button');
        button.className = 'chat-button';
        button.innerHTML = '💡';
        button.setAttribute('aria-label', 'Yordam kerak?');
        button.title = 'Yordam kerak?';
        
        const widget = document.createElement('div');
        widget.className = 'chat-widget';
        widget.appendChild(button);
        
        document.body.appendChild(widget);
        
        button.addEventListener('click', () => this.openModal());
    }

    createModal() {
        const modalHTML = `
            <div class="chat-modal" id="chatModal">
                <div class="chat-modal-content">
                    <div class="chat-modal-header">
                        <h3 class="chat-modal-title">💡 Yordam kerak?</h3>
                        <button class="chat-close" id="chatClose">&times;</button>
                    </div>
                    <div class="chat-modal-body">
                        <div class="chat-tabs">
                            <button class="chat-tab active" data-tab="webchat">💬 Chat</button>
                            <button class="chat-tab" data-tab="phone">📞 Qo'ng'iroq</button>
                        </div>
                        
                        <div id="chatAlert" class="chat-alert" style="display: none;"></div>
                        
                        <!-- Webchat Tab -->
                        <div class="chat-tab-content active" id="webchat-content">
                            <form class="chat-form" id="webchatForm">
                                <textarea 
                                    class="chat-textarea" 
                                    id="webchatMessage" 
                                    placeholder="Savolingizni yozing..."
                                    required
                                ></textarea>
                                <button type="submit" class="chat-submit" id="webchatSubmit">
                                    Yuborish
                                </button>
                            </form>
                        </div>
                        
                        <!-- Phone Tab -->
                        <div class="chat-tab-content" id="phone-content">
                            <form class="chat-form" id="phoneForm">
                                <input 
                                    type="tel" 
                                    class="chat-input" 
                                    id="phoneNumber" 
                                    placeholder="+998901234567"
                                    pattern="^\\+998\\d{9}$"
                                    required
                                />
                                <small style="color: #666; font-size: 12px;">
                                    Sizga qo'ng'iroq qilamiz. Format: +998XXXXXXXXX
                                </small>
                                <button type="submit" class="chat-submit" id="phoneSubmit">
                                    Qo'ng'iroq so'rash
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('chatModal');
    }

    attachEventListeners() {
        // Modal yopish
        const closeBtn = document.getElementById('chatClose');
        closeBtn.addEventListener('click', () => this.closeModal());
        
        // Modal tashqarisiga bosish
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // ESC tugmasi
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display === 'block') {
                this.closeModal();
            }
        });

        // Tab switching
        const tabs = document.querySelectorAll('.chat-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // Form submissions
        document.getElementById('webchatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitWebchat();
        });

        document.getElementById('phoneForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitPhone();
        });
    }

    openModal() {
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        setTimeout(() => {
            const firstInput = this.modal.querySelector('.chat-tab-content.active input, .chat-tab-content.active textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }, 100);
    }

    closeModal() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
        this.clearAlert();
        this.resetForms();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.chat-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.chat-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-content`).classList.add('active');

        this.currentTab = tabName;
        this.clearAlert();
    }

    async submitWebchat() {
        const message = document.getElementById('webchatMessage').value.trim();
        const submitBtn = document.getElementById('webchatSubmit');
        
        if (!message) {
            this.showAlert('Iltimos, xabar yozing', 'error');
            return;
        }

        this.setLoading(submitBtn, true);
        this.clearAlert();

        try {
            const response = await fetch('/contact/webchat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert(result.message, 'success');
                document.getElementById('webchatMessage').value = '';
                
                // Close modal after 2 seconds
                setTimeout(() => {
                    this.closeModal();
                }, 2000);
            } else {
                this.showAlert(result.error || 'Xatolik yuz berdi', 'error');
            }
        } catch (error) {
            this.showAlert('Tarmoq xatoligi. Qaytadan urinib ko\\'ring.', 'error');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    async submitPhone() {
        const phone = document.getElementById('phoneNumber').value.trim();
        const submitBtn = document.getElementById('phoneSubmit');
        
        if (!phone) {
            this.showAlert('Iltimos, telefon raqamingizni kiriting', 'error');
            return;
        }

        // Validate phone format
        const phonePattern = /^\\+998\\d{9}$/;
        if (!phonePattern.test(phone)) {
            this.showAlert('Telefon raqami +998 bilan boshlanishi va 13 ta raqamdan iborat bo\\'lishi kerak', 'error');
            return;
        }

        this.setLoading(submitBtn, true);
        this.clearAlert();

        try {
            const response = await fetch('/contact/phone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ phone: phone })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert(result.message, 'success');
                document.getElementById('phoneNumber').value = '';
                
                // Close modal after 3 seconds
                setTimeout(() => {
                    this.closeModal();
                }, 3000);
            } else {
                this.showAlert(result.error || 'Xatolik yuz berdi', 'error');
            }
        } catch (error) {
            this.showAlert('Tarmoq xatoligi. Qaytadan urinib ko\\'ring.', 'error');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    showAlert(message, type) {
        const alert = document.getElementById('chatAlert');
        alert.textContent = message;
        alert.className = `chat-alert ${type}`;
        alert.style.display = 'block';
    }

    clearAlert() {
        const alert = document.getElementById('chatAlert');
        alert.style.display = 'none';
    }

    setLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.textContent = 'Yuborilmoqda...';
        } else {
            button.disabled = false;
            button.textContent = button.id === 'webchatSubmit' ? 'Yuborish' : 'Qo\\'ng\\'iroq so\\'rash';
        }
    }

    resetForms() {
        document.getElementById('webchatForm').reset();
        document.getElementById('phoneForm').reset();
    }
}

// Initialize chat widget when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatWidget();
});