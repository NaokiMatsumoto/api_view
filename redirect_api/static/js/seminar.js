class SeminarSystem {
    constructor() {
        this.config = {
            selectors: {
                taskCheckbox: '.task-checkbox',
                taskItem: '.task-item',
                progressBar: '.progress-bar',
                seminarForm: 'form.seminar-form, form[id*="seminar"], .seminar-form form',
                priceField: 'input[name="price"], input[name="seminar_price"]',
                capacityField: 'input[name="capacity"], input[name="max_capacity"]'
            },
            animation: {
                taskScale: { duration: 150, scale: 0.98 },
                progressBar: { delay: 500 },
                submitTimeout: 10000,
                notificationDuration: 3000
            },
            limits: {
                maxCapacity: 999999,
                minCapacity: 1
            }
        };
        
        // イベントリスナー管理用
        this.eventListeners = [];
        this.activeTimeouts = new Set();
    }

    addListener(element, type, handler) {
        if (!element || !element.addEventListener) {
            return;
        }
        element.addEventListener(type, handler);
        this.eventListeners.push({ element, type, handler });
    }

    /**
     * システム初期化
     */
    init() {
        try {
            this.initTaskCheckboxes();
            this.initProgressBars();
            this.initFormValidation();
            this.initDateFields();
        } catch (error) {
            console.error('SeminarSystem initialization failed:', error);
        }
    }

    /**
     * タスクチェックボックスのアニメーション初期化
     */
    initTaskCheckboxes() {
        const taskCheckboxes = document.querySelectorAll(this.config.selectors.taskCheckbox);
        if (taskCheckboxes.length === 0) return;

        taskCheckboxes.forEach(checkbox => {
            const handler = this.handleTaskCheckboxChange.bind(this);
            this.addListener(checkbox, 'change', handler);
        });
    }

    /**
     * タスクチェックボックス変更時の処理
     */
    handleTaskCheckboxChange(event) {
        const taskItem = event.target.closest(this.config.selectors.taskItem);
        if (!taskItem) return;

        taskItem.style.transition = 'all 0.3s ease-in-out';
        if (event.target.checked) {
            taskItem.style.transform = `scale(${this.config.animation.taskScale.scale})`;
            setTimeout(() => {
                if (taskItem.parentNode) { // DOM存在チェック
                    taskItem.style.transform = 'scale(1)';
                }
            }, this.config.animation.taskScale.duration);
        }
    }

    /**
     * プログレスバーのアニメーション初期化
     */
    initProgressBars() {
        const progressBars = document.querySelectorAll(this.config.selectors.progressBar);
        if (progressBars.length === 0) return;

        progressBars.forEach(bar => {
            const width = bar.style.width;
            if (width && width !== '0%') {
                bar.style.width = '0%';
                bar.style.transition = 'width 0.8s ease-in-out';
                setTimeout(() => {
                    if (bar.parentNode) { // DOM存在チェック
                        bar.style.width = width;
                    }
                }, this.config.animation.progressBar.delay);
            }
        });
    }

    initFormValidation() {
        const seminarForms = document.querySelectorAll(this.config.selectors.seminarForm);
        
        seminarForms.forEach(form => {
            try {
                this.setupFormValidation(form);
            } catch (error) {
                console.error('Form validation setup failed:', error);
            }
        });
    }

    /**
     * 個別フォームのバリデーション設定
     */
    setupFormValidation(form) {
        const inputs = form.querySelectorAll('input[name], select[name], textarea[name]');
        const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        // リアルタイムバリデーション
        inputs.forEach(input => {
            const blurHandler = () => this.validateField(input);
            const inputHandler = () => {
                if (input.classList.contains('border-red-300')) {
                    this.validateField(input);
                }
            };

            this.addListener(input, 'blur', blurHandler);
            this.addListener(input, 'input', inputHandler);
        });

        // 特殊フィールドの初期化
        this.initPriceField(form);
        this.initCapacityField(form);

        // フォーム送信時の処理
        const submitHandler = (e) => this.handleFormSubmit(e, form, inputs, requiredInputs);
        this.addListener(form, 'submit', submitHandler);
    }

    /**
     * 開催日フィールドの初期化（追加/削除・軽い検証）
     */
    initDateFields() {
        const container = document.getElementById('dates-container');
        const addBtn = document.getElementById('add-date-btn');
        if (!container || !addBtn) return;

        // 今日の日付（YYYY-MM-DD）を計算
        const toYMD = (d) => {
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd}`;
        };
        const todayStr = toYMD(new Date());

        const createRow = (value = '') => {
            const row = document.createElement('div');
            row.className = 'date-row flex items-center gap-3';
            row.innerHTML = `
                    <input type="date" name="dates[]" ${value ? `value="${value}"` : ''} min="${todayStr}" class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition duration-150 ease-in-out form-input date-input">
                <button type="button" class="remove-date-btn text-red-600 hover:text-red-700 px-3 py-2 rounded border border-red-200 hover:border-red-300">削除</button>
            `;
            return row;
        };

        const onAdd = () => {
            container.appendChild(createRow());
        };
        this.addListener(addBtn, 'click', onAdd);

        const onClick = (e) => {
            const btn = e.target.closest('.remove-date-btn');
            if (!btn) return;
            const row = btn.closest('.date-row');
            if (row && container.children.length > 1) {
                row.remove();
            } else if (row) {
                // 最低1行は維持: 値だけクリア
                const input = row.querySelector('input.date-input');
                if (input) input.value = '';
            }
        };
        this.addListener(container, 'click', onClick);

        const validateDates = () => {
            const inputs = Array.from(container.querySelectorAll('input.date-input'));
            const values = inputs.map(i => i.value).filter(Boolean);
            const seen = new Set();
            const dupes = new Set();
            values.forEach(v => {
                if (seen.has(v)) dupes.add(v); else seen.add(v);
            });

            let allValid = true;
            inputs.forEach(input => {
                const v = input.value;
                let valid = true;
                if (v) {
                    // 形式
                    if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) valid = false;
                    // 過去日
                    if (valid && v < todayStr) valid = false;
                    // 重複
                    if (valid && dupes.has(v)) valid = false;
                }

                if (!valid) {
                    input.classList.add('border-red-300');
                    input.classList.remove('border-green-300');
                    allValid = false;
                } else if (v) {
                    input.classList.remove('border-red-300');
                    input.classList.add('border-green-300');
                } else {
                    input.classList.remove('border-red-300', 'border-green-300');
                }
            });
            return allValid;
        };

        const onInput = (e) => {
            const input = e.target.closest('input.date-input');
            if (!input) return;
            validateDates();
        };
        this.addListener(container, 'input', onInput);

        // 既存行にもmin属性を反映
        container.querySelectorAll('input.date-input').forEach(input => {
            input.setAttribute('min', todayStr);
        });

        // 送信前の総合検証をフック
        const forms = document.querySelectorAll(this.config.selectors.seminarForm);
        forms.forEach(form => {
            const submitValidate = (e) => {
                const ok = validateDates();
                if (!ok) {
                    e.preventDefault();
                    this.showNotification('開催日は重複不可・過去日不可です。修正してください。', 'error');
                    // 送信ボタンが無効化されている場合は再有効化（UX 改善）
                    try {
                        // クリックされた送信ボタンのみ先に有効化（対応ブラウザ）
                        if (e.submitter) {
                            e.submitter.disabled = false;
                        }
                    } catch (_) { /* noop */ }

                    // 念のため全送信ボタンを再有効化
                    form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(btn => {
                        btn.disabled = false;
                    });

                    // 事前に設定したローディング解除タイマーもクリア
                    try {
                        this.activeTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
                        this.activeTimeouts.clear();
                    } catch (_) { /* noop */ }

                    this.scrollToFirstError(form);
                }
            };
            this.addListener(form, 'submit', submitValidate);
        });
    }

    /**
     * 価格フィールドの初期化（修正版）
     */
    initPriceField(form) {
        const priceField = form.querySelector(this.config.selectors.priceField);
        if (!priceField) return;

        const inputHandler = this.handlePriceInput.bind(this);
        const blurHandler = this.handlePriceBlur.bind(this);
        
        this.addListener(priceField, 'input', inputHandler);
        this.addListener(priceField, 'blur', blurHandler);
    }

    /**
     * 価格フィールド入力処理（修正版）
     */
    handlePriceInput(event) {
        // 数値のみを抽出
        let value = event.target.value.replace(/[^\d]/g, '');
        event.target.value = value;
    }

    /**
     * 価格フィールドフォーカスアウト処理（修正版）
     */
    handlePriceBlur(event) {
        // 既に数値のみなので、そのまま保持
        const value = event.target.value;
        if (value) {
            // 数値として有効かチェック
            const numericValue = parseInt(value, 10);
            if (!isNaN(numericValue) && numericValue >= 0) {
                event.target.value = numericValue.toString();
            } else {
                event.target.value = '';
            }
        }
    }

    /**
     * 定員フィールドの初期化
     */
    initCapacityField(form) {
        const capacityField = form.querySelector(this.config.selectors.capacityField);
        if (!capacityField) return;

        const inputHandler = this.handleCapacityInput.bind(this);
        const blurHandler = (event) => {
            if (event.target.value && parseInt(event.target.value, 10) < this.config.limits.minCapacity) {
                event.target.value = this.config.limits.minCapacity.toString();
                this.validateField(event.target);
            }
        };
        
        this.addListener(capacityField, 'input', inputHandler);
        this.addListener(capacityField, 'blur', blurHandler);
    }

    /**
     * 定員フィールド入力時の処理
     */
    handleCapacityInput(event) {
        // 数値のみ抽出
        let value = event.target.value.replace(/[^\d]/g, '');
        
        if (value) {
            let numericValue = parseInt(value, 10);
            
            // 範囲チェック
            if (numericValue < this.config.limits.minCapacity) {
                numericValue = this.config.limits.minCapacity;
            }
            if (numericValue > this.config.limits.maxCapacity) {
                numericValue = this.config.limits.maxCapacity;
            }
            
            event.target.value = numericValue.toString();
        } else {
            event.target.value = '';
        }
    }

    /**
     * フォーム送信処理
     */
    handleFormSubmit(event, form, inputs, requiredInputs) {
        let isFormValid = true;

        // バリデーション実行
        requiredInputs.forEach(input => {
            if (!input.checkValidity()) {
                this.validateField(input);
                isFormValid = false;
            }
        });
        
        inputs.forEach(input => {
            if (!input.hasAttribute('required') && input.value && !input.checkValidity()) {
                this.validateField(input);
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            event.preventDefault();
            form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(btn => {
                btn.disabled = false;
            });
            this.scrollToFirstError(form);
        } else {
            // 送信開始時に二重送信防止（クリック時ではなく submit 時に実施）
            if (form.dataset.submitting === '1') {
                event.preventDefault();
                return;
            }
            form.dataset.submitting = '1';

            const buttons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            buttons.forEach(btn => (btn.disabled = true));

            const timeoutId = window.setTimeout(() => {
                // 遷移しなかった場合のセーフティ
                buttons.forEach(btn => (btn.disabled = false));
                form.dataset.submitting = '';
                this.activeTimeouts.delete(timeoutId);
            }, this.config.animation.submitTimeout);
            this.activeTimeouts.add(timeoutId);
        }
    }

    /**
     * 最初のエラーフィールドまでスクロール
     */
    scrollToFirstError(form) {
        const firstError = form.querySelector('.border-red-300');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => firstError.focus(), 300); // スクロール完了後にフォーカス
        }
    }

    /**
     * フィールドバリデーション
     */
    validateField(field) {
        const isValid = field.checkValidity();
        const errorElement = field.parentNode?.querySelector('.text-red-600');
        
        if (isValid) {
            field.classList.remove('border-red-300');
            field.classList.add('border-green-300');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        } else {
            field.classList.remove('border-green-300');
            field.classList.add('border-red-300');
            if (errorElement) {
                errorElement.style.display = 'block';
            }
        }
    }

    /**
     * 通知メッセージを表示（修正版）
     */
    showNotification(message, type = 'info') {
        if (!message) return;
        
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'warning' ? 'bg-yellow-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // 表示アニメーション
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
        });
        
        // 自動削除
        const hideTimeout = setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)'; // 修正: translateX(full) → translateX(100%)
                
                const removeTimeout = setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
                
                // タイムアウトIDを保存してクリーンアップ可能にする
                notification.dataset.removeTimeoutId = removeTimeout;
            }
        }, this.config.animation.notificationDuration);
        
        notification.dataset.hideTimeoutId = hideTimeout;
        
        // クリックで手動削除
        notification.addEventListener('click', () => {
            if (notification.dataset.hideTimeoutId) {
                clearTimeout(parseInt(notification.dataset.hideTimeoutId));
            }
            if (notification.dataset.removeTimeoutId) {
                clearTimeout(parseInt(notification.dataset.removeTimeoutId));
            }
            
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        });
    }

    destroy() {
        // 全てのイベントリスナーを削除
        this.eventListeners.forEach(({ element, type, handler }) => {
            if (element && element.removeEventListener) {
                element.removeEventListener(type, handler);
            }
        });
        this.eventListeners = [];

        // アクティブなタイムアウトをクリア
        this.activeTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
        this.activeTimeouts.clear();

        // アクティブな通知を削除
        document.querySelectorAll('[data-hide-timeout-id]').forEach(notification => {
            const hideTimeoutId = notification.dataset.hideTimeoutId;
            const removeTimeoutId = notification.dataset.removeTimeoutId;
            
            if (hideTimeoutId) clearTimeout(parseInt(hideTimeoutId));
            if (removeTimeoutId) clearTimeout(parseInt(removeTimeoutId));
            
            if (notification.parentNode) {
                notification.remove();
            }
        });
    }
}

// システム初期化
document.addEventListener('DOMContentLoaded', function() {
    const seminarSystem = new SeminarSystem();
    seminarSystem.init();
    
    // グローバルアクセス用
    window.SeminarSystem = {
        showNotification: seminarSystem.showNotification.bind(seminarSystem),
        instance: seminarSystem,
        destroy: seminarSystem.destroy.bind(seminarSystem)
    };
    
    // ページ離脱時のクリーンアップ
    window.addEventListener('beforeunload', () => {
        if (window.SeminarSystem?.instance) {
            window.SeminarSystem.destroy();
        }
    });
});
