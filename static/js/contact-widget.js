// Contact Widget JavaScript
let webchatOpen = false;

function openWebchatWidget() {
    if (webchatOpen) return;
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'webchat-modal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="bi bi-chat-dots me-2"></i>Online Chat
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="chat-area" style="height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; background-color: #f9f9f9;">
                        <div class="message mb-3">
                            <div class="d-flex">
                                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 35px; height: 35px;">
                                    <i class="bi bi-headset"></i>
                                </div>
                                <div class="bg-white p-3 rounded shadow-sm">
                                    <p class="mb-0">Salom! Sizga qanday yordam bera olaman?</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <form id="webchat-form">
                        <div class="input-group">
                            <input type="text" class="form-control" id="webchat-input" placeholder="Xabaringizni yozing..." required>
                            <button class="btn btn-primary" type="submit">
                                <i class="bi bi-send"></i>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    webchatOpen = true;
    
    // Focus input
    setTimeout(() => {
        document.getElementById('webchat-input').focus();
    }, 500);
    
    // Handle form submission
    document.getElementById('webchat-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('webchat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        addWebchatMessage(message, 'user');
        input.value = '';
        
        try {
            const response = await fetch('/contact/webchat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                addWebchatMessage(data.message, 'support');
            } else {
                addWebchatMessage('Kechirasiz, xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.', 'support');
            }
        } catch (error) {
            addWebchatMessage('Aloqa xatosi. Iltimos, qayta urinib ko\'ring.', 'support');
        }
    });
    
    // Close event
    modal.addEventListener('hidden.bs.modal', () => {
        webchatOpen = false;
        modal.remove();
    });
}

function addWebchatMessage(message, sender) {
    const chatArea = document.getElementById('chat-area');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message mb-3';
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="d-flex justify-content-end">
                <div class="bg-primary text-white p-3 rounded shadow-sm me-3" style="max-width: 70%;">
                    <p class="mb-0">${message}</p>
                </div>
                <div class="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 35px; height: 35px;">
                    <i class="bi bi-person"></i>
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="d-flex">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 35px; height: 35px;">
                    <i class="bi bi-headset"></i>
                </div>
                <div class="bg-white p-3 rounded shadow-sm" style="max-width: 70%;">
                    <p class="mb-0">${message}</p>
                </div>
            </div>
        `;
    }
    
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function requestPhoneCall() {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'phone-modal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title">
                        <i class="bi bi-telephone me-2"></i>Telefon qo'ng'iroq so'rovi
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Telefon raqamingizni qoldiring, tez orada siz bilan bog'lanamiz.</p>
                    
                    <form id="phone-form">
                        <div class="mb-3">
                            <label for="phone-number" class="form-label">Telefon raqam</label>
                            <input type="tel" 
                                   class="form-control" 
                                   id="phone-number" 
                                   placeholder="+998901234567"
                                   pattern="^\\+998\\d{9}$"
                                   required>
                            <div class="form-text">+998 bilan boshlanishi kerak</div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="phone-message" class="form-label">Qo'shimcha xabar (ixtiyoriy)</label>
                            <textarea class="form-control" 
                                      id="phone-message" 
                                      rows="3"
                                      placeholder="Qanday masala bo'yicha aloqaga chiqishimiz kerak?"></textarea>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-success">
                                <i class="bi bi-telephone"></i> Qo'ng'iroq so'rash
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Focus input
    setTimeout(() => {
        document.getElementById('phone-number').focus();
    }, 500);
    
    // Handle form submission
    document.getElementById('phone-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const phone = document.getElementById('phone-number').value.trim();
        const message = document.getElementById('phone-message').value.trim();
        
        try {
            const response = await fetch('/contact/phone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify({ 
                    phone: phone,
                    message: message || 'Telefon qo\'ng\'iroq so\'rovi'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                bsModal.hide();
            } else {
                alert(data.error || 'Xatolik yuz berdi');
            }
        } catch (error) {
            alert('Aloqa xatosi. Iltimos, qayta urinib ko\'ring.');
        }
    });
    
    // Close event
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}