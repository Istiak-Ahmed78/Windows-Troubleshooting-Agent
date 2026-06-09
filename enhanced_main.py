"""
AI PC Troubleshooting Agent
Enhanced Integrated Main Module
Uses LLM (via Ollama) when available, falls back to rule-based engine
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import os
import subprocess
from typing import Dict, List
from diagnostics import WindowsDiagnostics, format_bytes
from troubleshooting_engine import TroubleshootingEngine
from agent_loop import AgentLoop, ModelManager, OllamaProvider, OpenAICompatibleProvider, PROVIDER_PRESETS
from remediation_engine import RemediationEngine, TODO_STATE_FILE
from config import GUI_CONFIG


class EnhancedTroubleshootingAgent(ctk.CTk):
    """Enhanced troubleshooting agent with all features"""

    def __init__(self):
        super().__init__()

        self.title(GUI_CONFIG["window_title"])
        self.geometry(GUI_CONFIG["window_size"])

        ctk.set_appearance_mode(GUI_CONFIG["theme"])
        ctk.set_default_color_theme(GUI_CONFIG["color_theme"])

        self.diagnostics = WindowsDiagnostics()
        self.engine = TroubleshootingEngine()
        self.agent_loop = AgentLoop()
        self.remediation = RemediationEngine()
        self.current_diagnostics = None
        self.using_llm = False

        self.create_widgets()
        self.show_welcome_message()
        self.api_config = self.load_api_config()
        self.apply_provider_config(self.api_config)
        self.after(100, self.check_llm_availability)

        # Check if we're resuming after a restart
        if RemediationEngine.was_restarted():
            self.after(2000, self._resume_after_restart)

    def create_widgets(self):
        """Create all UI widgets"""
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        header = ctk.CTkFrame(main, fg_color=GUI_CONFIG["header_color"])
        header.pack(fill="x", padx=0, pady=0)

        title = ctk.CTkLabel(
            header,
            text=GUI_CONFIG["window_title"],
            font=("Helvetica", 24, "bold"),
            text_color=GUI_CONFIG["primary_color"]
        )
        title.pack(pady=15)

        subtitle = ctk.CTkLabel(
            header,
            text="Intelligent System Diagnostics & Troubleshooting",
            font=("Helvetica", 12),
            text_color="#888888"
        )
        subtitle.pack(pady=(0, 5))

        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.mode_label = ctk.CTkLabel(
            mode_frame, text="Mode: Checking...",
            font=("Helvetica", 10), text_color="#ffaa00"
        )
        self.mode_label.pack(side="left", padx=(0, 10))

        self.provider_options = ["Rule-based", "Local Ollama"] + list(PROVIDER_PRESETS.keys())
        self.provider_var = tk.StringVar(value="Rule-based")
        self.provider_selector = ctk.CTkOptionMenu(
            mode_frame, values=self.provider_options, variable=self.provider_var,
            width=180, height=24, font=("Helvetica", 10),
            command=self._on_provider_selected
        )
        self.provider_selector.pack(side="left", padx=(0, 10))

        self.mode_toggle_btn = ctk.CTkButton(
            mode_frame, text="Switch to AI", width=100, height=24,
            command=self._toggle_mode, font=("Helvetica", 10)
        )
        self.mode_toggle_btn.pack(side="left", padx=(0, 10))

        settings_btn = ctk.CTkButton(
            mode_frame, text="Settings", width=80, height=24,
            command=self.open_settings, font=("Helvetica", 10)
        )
        settings_btn.pack(side="right")

        self.progress_frame = ctk.CTkFrame(main, fg_color="transparent", height=0)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=("Helvetica", 10), text_color="#888888")
        self.progress_label.pack(fill="x", padx=20, pady=(0, 2))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=6, mode="determinate")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 5))
        self.progress_bar.set(0)

        content = ctk.CTkFrame(main)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(content)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        chat_label = ctk.CTkLabel(left, text="Chat Interface", font=("Helvetica", 14, "bold"))
        chat_label.pack(pady=(0, 10))

        self.chat = scrolledtext.ScrolledText(
            left, height=20, width=60,
            font=("Courier", 10),
            bg=GUI_CONFIG["background_color"],
            fg=GUI_CONFIG["text_color"],
            insertbackground=GUI_CONFIG["primary_color"]
        )
        self.chat.pack(fill="both", expand=True, pady=(0, 10))
        self.chat.config(state="disabled")

        self.chat.tag_config("user", foreground=GUI_CONFIG["primary_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("agent", foreground=GUI_CONFIG["success_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("reasoning", foreground=GUI_CONFIG["warning_color"], font=("Courier", 9, "italic"))
        self.chat.tag_config("finding", foreground=GUI_CONFIG["error_color"], font=("Courier", 10))
        self.chat.tag_config("solution", foreground=GUI_CONFIG["info_color"], font=("Courier", 10))
        self.chat.tag_config("recommendation", foreground=GUI_CONFIG["info_color"], font=("Courier", 10))
        self.chat.tag_config("action", foreground=GUI_CONFIG["primary_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("header", foreground=GUI_CONFIG["success_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("tool", foreground="#d4a0ff", font=("Courier", 9, "italic"))
        self.chat.tag_config("info", foreground="#888888", font=("Courier", 9))

        input_frame = ctk.CTkFrame(left)
        input_frame.pack(fill="x")

        self.input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Describe your PC issue...",
            font=("Helvetica", 11),
            height=40
        )
        self.input.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.input.bind("<Return>", lambda e: self.process_user_input())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            command=self.process_user_input,
            font=("Helvetica", 11, "bold")
        )
        self.send_btn.pack(side="left")

        right = ctk.CTkFrame(content, width=350)
        right.pack(side="right", fill="both", padx=(5, 0))
        right.pack_propagate(False)

        diag_label = ctk.CTkLabel(right, text="System Diagnostics", font=("Helvetica", 14, "bold"))
        diag_label.pack(pady=(0, 10))

        self.diagnose_btn = ctk.CTkButton(
            right,
            text="> Run Full Diagnostics",
            command=self.run_diagnostics,
            font=("Helvetica", 11, "bold"),
            height=35,
            fg_color=GUI_CONFIG["primary_color"],
            text_color="#000000"
        )
        self.diagnose_btn.pack(fill="x", pady=(0, 10))

        self.system_info = scrolledtext.ScrolledText(
            right, height=35, width=40,
            font=("Courier", 9),
            bg=GUI_CONFIG["background_color"],
            fg=GUI_CONFIG["text_color"]
        )
        self.system_info.pack(fill="both", expand=True)
        self.system_info.config(state="disabled")

        self.system_info.tag_config("header", foreground=GUI_CONFIG["primary_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("good", foreground=GUI_CONFIG["success_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("warning", foreground=GUI_CONFIG["warning_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("critical", foreground=GUI_CONFIG["error_color"], font=("Courier", 9, "bold"))

        self.status = tk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(main, textvariable=self.status, font=("Helvetica", 10), text_color="#888888")
        status_bar.pack(fill="x", padx=10, pady=(5, 10))

    def _show_progress(self, visible: bool = True, label: str = "", pct: float = 0):
        if visible:
            self.progress_frame.configure(height=50)
            self.progress_label.configure(text=label)
            self.progress_bar.set(pct / 100)
            self.progress_frame.pack(fill="x", padx=0, pady=0)
        else:
            self._hide_progress()
        self.update()

    def _hide_progress(self):
        self.progress_frame.configure(height=0)
        self.progress_frame.pack_forget()
        self.update()

    def _update_progress(self, label: str, pct: float = None):
        self.progress_label.configure(text=label)
        if pct is not None:
            self.progress_bar.set(pct / 100)
        self.update()

    def check_llm_availability(self):
        """Check saved API config or Ollama, then prompt for provider setup."""
        self._show_progress(True, "Checking LLM configuration...", 10)
        self.status.set("Checking configuration...")

        # Step 1: Is an API provider already configured with a key?
        api_key = self.api_config.get("api_key", "").strip()
        provider_name = self.api_config.get("provider", "")
        if api_key and provider_name and provider_name != "ollama":
            self._update_progress(f"Using saved provider: {provider_name}", 50)
            self.using_llm = True
            self._show_progress(False)
            self.add_chat("agent", f"LLM mode active ({provider_name})", "info")
            self.update_mode_label()
            self.status.set("Ready")
            return

        # Step 2: Check for Ollama (local model)
        self._update_progress("Checking for Ollama...", 20)
        ollama_models = []
        if self.agent_loop.is_ollama_available():
            ollama_models = self.agent_loop.list_available_models()

        self._show_progress(False)

        # Step 3: Ask user which provider to use
        msg = "Configure an AI provider for better troubleshooting?\n\n"
        if ollama_models:
            model_str = ", ".join(m.replace(":latest", "") for m in ollama_models[:3])
            msg += f"Local Ollama detected ({model_str})\n"
            msg += "- Can use offline, but may be slow on this PC\n\n"
        msg += "Options:\n"
        msg += "Yes = Set up cloud AI provider (recommended — Groq has free tier)\n"
        msg += "No = Use rule-based engine (no AI)\n"
        if ollama_models:
            msg += "Cancel = Use local Ollama"

        buttons = messagebox.askyesnocancel("AI Provider Setup", msg)

        if buttons is True:
            self.after(100, self.open_settings)
            return
        elif buttons is None and ollama_models:
            self.using_llm = True
            self.add_chat("agent", "Using local Ollama (responses may be slow)", "info")
        else:
            self.using_llm = False
            self.add_chat("agent", "Rule-based mode active", "info")
            self.add_chat("info", "Click Settings to configure an AI provider (Groq has free tier)")

        self.update_mode_label()
        self.status.set("Ready")

    def _prompt_download_model(self):
        """Ask user if they want to download a model"""
        free_gb = ModelManager.get_free_space_gb()
        recommended = ModelManager.recommend_model()
        if recommended:
            model_size = ModelManager.MODEL_SIZES[recommended]
            msg = (
                f"Ollama is running but no models are downloaded.\n"
                f"Download {recommended} ({model_size:.1f} GB)?\n\n"
                f"Free space: {free_gb:.1f} GB"
            )
            if messagebox.askyesno("Download LLM Model", msg):
                self._run_model_download(recommended)

    def _run_auto_setup(self, model: str):
        """Download Ollama installer + install + pull model (runs in thread, updates progress bar)"""
        def setup():
            self.send_btn.configure(state="disabled")
            self.diagnose_btn.configure(state="disabled")
            self._show_progress(True, "Starting auto-setup...", 0)
            try:
                self.add_chat("agent", f"Auto-setup: Ollama + {model}", "header")

                # --- Phase 1: Download installer ---
                self._update_progress("Creating temp directory...", 2)
                installer_dir = os.path.join(os.environ["TEMP"], "opencode_ollama")
                os.makedirs(installer_dir, exist_ok=True)
                installer_path = os.path.join(installer_dir, "OllamaSetup.exe")

                self._update_progress("Downloading Ollama installer (600 MB)...", 5)
                self.add_chat("info", "Downloading Ollama installer (~600 MB)...")

                def dl_progress(pct, downloaded, total):
                    mb_dl = downloaded / (1024 * 1024)
                    mb_total = total / (1024 * 1024)
                    self._update_progress(f"Downloading Ollama... {mb_dl:.0f}/{mb_total:.0f} MB ({pct}%)", 5 + pct * 0.5)

                ModelManager.download_file(ModelManager.OLLAMA_DOWNLOAD_URL, installer_path, dl_progress)
                self._update_progress("Download complete!", 55)

                # --- Phase 2: Install ---
                self._update_progress("Installing Ollama (this may take a minute)...", 58)
                self.add_chat("info", "Installing Ollama...")

                def inst_progress(msg):
                    self._update_progress(f"Installing: {msg}", 60)

                ModelManager.install_ollama(installer_path, inst_progress)
                self._update_progress("Ollama installed! Starting service...", 70)

                ollama_exe = ModelManager.get_ollama_exe_path()
                if ollama_exe:
                    subprocess.Popen([ollama_exe], creationflags=subprocess.CREATE_NO_WINDOW)
                    for i in range(6):
                        time.sleep(1)
                        self._update_progress(f"Waiting for Ollama to start... ({i+1}/6)", 70 + i * 2)
                        if self.agent_loop.is_ollama_available():
                            break

                if not self.agent_loop.is_ollama_available():
                    self._hide_progress()
                    self.add_chat("finding", "Ollama installed but not responding.")
                    self.add_chat("solution", "Restart the app or run Ollama manually.")
                    self.status.set("Setup incomplete")
                    return

                self._update_progress("Ollama is running!", 82)

                # --- Phase 3: Download model ---
                self._download_model_with_progress(model)

            except Exception as e:
                self._hide_progress()
                self.add_chat("finding", f"Auto-setup failed: {e}")
                self.status.set("Setup failed")
            finally:
                self.send_btn.configure(state="normal")
                self.diagnose_btn.configure(state="normal")

        thread = threading.Thread(target=setup)
        thread.daemon = True
        thread.start()

    def _download_model_with_progress(self, model: str):
        """Download model with progress bar updates (call from thread)"""
        self._update_progress(f"Downloading {model} (this may take 5-30 minutes)...", 83)
        self.add_chat("info", f"Downloading {model}...")

        def on_progress(line):
            line = line.strip()
            if "%" in line:
                try:
                    pct_str = line.split()[-1].replace("%", "")
                    pct = float(pct_str)
                    display = line[:50] + "..." if len(line) > 50 else line
                    self._update_progress(f"Downloading {model}: {display}", 83 + pct * 0.15)
                except:
                    self._update_progress(f"Downloading {model}: {line[:60]}", 85)
            else:
                self._update_progress(f"Downloading {model}: {line[:60]}", 85)

        success = ModelManager.pull_model(model, on_progress)

        if success:
            self.using_llm = True
            self.agent_loop._ollama_available = True
            self.agent_loop.model = model
            self._update_progress(f"{model} downloaded!", 100)
            time.sleep(0.5)
            self._hide_progress()
            self.update_mode_label()
            self.add_chat("agent", f"{model} downloaded! Switching to LLM mode.", "header")
        else:
            self._hide_progress()
            self.add_chat("finding", f"Failed to download {model}")
        self.status.set("Ready")

    def _run_model_download(self, model: str):
        """Download an Ollama model (runs in thread)"""
        def download():
            self.send_btn.configure(state="disabled")
            try:
                self._show_progress(True, f"Downloading {model}...", 0)
                self._download_model_with_progress(model)
            except Exception as e:
                self._hide_progress()
                self.add_chat("finding", f"Download failed: {e}")
                self.status.set("Ready")
            finally:
                self.send_btn.configure(state="normal")

        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()

    def update_mode_label(self):
        if not hasattr(self, 'mode_label'):
            return
        if self.using_llm:
            provider = self.agent_loop.active_provider
            pname = provider.name if provider else "Ollama"
            self.mode_label.configure(text=f"Mode: {pname}", text_color="#00ff88")
            self.mode_toggle_btn.configure(text="Switch to Rule-based")
            for opt in self.provider_selector.cget("values"):
                if opt.lower() in pname.lower() or pname.lower() in opt.lower():
                    self.provider_var.set(opt)
                    break
            else:
                self.provider_var.set("Rule-based")
        else:
            self.mode_label.configure(text="Mode: Rule-based (fallback)", text_color="#ffaa00")
            self.mode_toggle_btn.configure(text="Switch to AI")
            self.provider_var.set("Rule-based")

    def _toggle_mode(self):
        if self.using_llm:
            self.using_llm = False
            self.add_chat("info", "Switched to rule-based mode")
        else:
            self.using_llm = self.agent_loop.active_provider is not None
            if self.using_llm:
                pname = self.agent_loop.active_provider.name
                self.add_chat("info", f"Switched to AI mode ({pname})")
            else:
                self.add_chat("finding", "No AI provider configured. Go to Settings to add one.")
        self.update_mode_label()

    def _on_provider_selected(self, choice: str):
        if choice == "Rule-based":
            self.using_llm = False
            self.add_chat("info", "Switched to rule-based mode")
        elif choice == "Local Ollama":
            if self.agent_loop.is_ollama_available():
                models = self.agent_loop.list_available_models()
                if models:
                    self.agent_loop.set_providers([OllamaProvider(url=self.agent_loop.ollama_url)])
                    self.agent_loop.model = models[0]
                    self.using_llm = True
                    self.add_chat("info", f"Switched to local Ollama ({models[0]})")
                else:
                    self.add_chat("finding", "Ollama has no models. Pull one via Settings.")
                    self.provider_var.set("Rule-based")
                    return
            else:
                self.add_chat("finding", "Ollama is not running. Start it or check Settings.")
                self.provider_var.set("Rule-based")
                return
        elif choice in PROVIDER_PRESETS:
            api_key = self.api_config.get("api_key", "").strip()
            saved_provider = self.api_config.get("provider", "")
            if saved_provider == choice and api_key:
                preset = PROVIDER_PRESETS[choice]
                base_url = self.api_config.get("base_url") or preset["base_url"]
                model = self.api_config.get("model") or preset["default_model"]
                provider = OpenAICompatibleProvider(api_key, base_url, model)
                self.agent_loop.set_providers([provider])
                self.agent_loop.model = model
                self.using_llm = True
                self.add_chat("info", f"Switched to {choice} ({model})")
            else:
                self.add_chat("info", f"Configure {choice} via Settings first")
                self.open_settings()
                return
        else:
            return
        self.update_mode_label()
        self.status.set("Ready")

    def show_welcome_message(self):
        """Show welcome message"""
        self.add_chat("agent", "Welcome to AI PC Troubleshooting Agent!")
        self.add_chat("agent", "I can help diagnose issues like:")
        self.add_chat("agent", "  - System running slow")
        self.add_chat("agent", "  - Applications won't open")
        self.add_chat("agent", "  - Low disk space")
        self.add_chat("agent", "  - Network problems")
        self.add_chat("agent", '\nTry: "My PC is slow", "Postman wont open", "disk full", or "scan for virus"')

    def add_chat(self, role: str, message: str, tag: str = "info"):
        """Add message to chat"""
        self.chat.config(state="normal")
        if role == "user":
            self.chat.insert("end", f"\nYou: ", "user")
            self.chat.insert("end", f"{message}\n", tag)
        elif role == "agent":
            self.chat.insert("end", f"\nAgent: ", "agent")
            self.chat.insert("end", f"{message}\n", tag)
        elif role == "reasoning":
            self.chat.insert("end", f"\n  ", "reasoning")
            self.chat.insert("end", f"{message}\n", "reasoning")
        elif role == "finding":
            self.chat.insert("end", f"\n  {message}\n", "finding")
        elif role == "solution":
            self.chat.insert("end", f"\n  {message}\n", "solution")
        elif role == "recommendation":
            self.chat.insert("end", f"\n  {message}\n", "recommendation")
        elif role == "action":
            self.chat.insert("end", f"\n[ACTION] {message}\n", "action")
        elif role == "header":
            self.chat.insert("end", f"\n{message}\n", "header")
        elif role == "tool":
            self.chat.insert("end", f"\n  [TOOL] {message}\n", "tool")
        elif role == "info":
            self.chat.insert("end", f"\n{message}\n", "info")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def process_user_input(self):
        """Process user message"""
        message = self.input.get().strip()
        if not message:
            return

        self.add_chat("user", message)
        self.input.delete(0, "end")
        self.send_btn.configure(state="disabled")

        # Handle actionable commands
        issue_lower = message.lower().strip()
        if issue_lower in ["scan for virus", "scan for malware", "run virus scan", "run defender scan"]:
            thread = threading.Thread(target=self.execute_defender_scan)
            thread.daemon = True
            thread.start()
            return
        if issue_lower in ["check disk", "run chkdsk", "check my disk"]:
            thread = threading.Thread(target=self.execute_chkdsk)
            thread.daemon = True
            thread.start()
            return
        if issue_lower in ["clean up", "disk cleanup", "run disk cleanup"]:
            import subprocess
            subprocess.Popen(["cleanmgr.exe"])
            self.add_chat("action", "Disk Cleanup launched")
            self.send_btn.configure(state="normal")
            return

        thread = threading.Thread(target=self.analyze_issue, args=(message,))
        thread.daemon = True
        thread.start()

    def analyze_issue(self, issue: str):
        """Analyze user issue"""
        try:
            self.status.set("Analyzing...")
            self.update_mode_label()

            if not self.using_llm:
                self.add_chat("agent", "Analyzing with rule-based engine...")
                time.sleep(0.3)
                self.current_diagnostics = self.diagnostics.get_system_info()
                analysis = self.engine.analyze_issue(issue, self.current_diagnostics)
                self.display_analysis(analysis)
                self.update_system_display()
                self.status.set("Ready")
                return

            self.add_chat("agent", "Analyzing with LLM... (this may take a moment)")
            time.sleep(0.3)
            self.current_diagnostics = self.diagnostics.get_system_info()

            def on_step(step_type, data):
                if step_type == "thinking":
                    self.add_chat("reasoning", data)
                    self.status.set(data[:60])
                elif step_type == "tool_call":
                    name = data.get("tool", "?")
                    args = data.get("args", {})
                    arg_summary = ", ".join(f"{k}={v}" for k, v in args.items())
                    self.add_chat("tool", f"{name}({arg_summary})")
                    self.status.set(f"Running: {name}...")
                elif step_type == "tool_result":
                    name = data.get("tool", "?")
                    result = data.get("result", {})
                    summary = str(result)[:80] if isinstance(result, dict) else str(result)[:80]
                    self.add_chat("tool", f"{name} -> {summary}")
                elif step_type == "answer":
                    self.add_chat("agent", data)

            analysis = self.agent_loop.analyze(issue, self.engine, step_callback=on_step)

            if analysis.get("from_rule_engine"):
                self.add_chat("info", "LLM unavailable — results from rule-based engine")
            else:
                tools_used = analysis.get("tools_used", [])
                if tools_used:
                    self.add_chat("info", f"LLM used tools: {', '.join(tools_used)}")

            self.display_analysis(analysis)
            self.update_system_display()
            self.status.set("Ready")

            todos = analysis.get("todos", [])
            if todos and not analysis.get("from_rule_engine"):
                self.add_chat("header", "=== Action Plan ===")
                self.add_chat("agent", f"I found {len(todos)} actionable step(s) to fix the issue.")
                self.add_chat("info", "I'll guide you through each step and ask for your permission.")
                self._execute_todos(todos, 0)

        except Exception as e:
            self.add_chat("agent", f"Error: {str(e)}", "finding")
            self.status.set("Error")
        finally:
            self.send_btn.configure(state="normal")

    def _resume_after_restart(self):
        state = self.remediation.load_state()
        if state and state.get("restart_initiated"):
            todos = state.get("todos", [])
            start_idx = state.get("current_index", 0)
            self.add_chat("agent", "Welcome back! I see you restarted your PC.", "header")
            self.add_chat("info", "Let me verify which steps were completed before continuing.")
            thread = threading.Thread(
                target=self._execute_todos,
                args=(todos, start_idx, "Resuming after restart...")
            )
            thread.daemon = True
            thread.start()
        else:
            self.add_chat("info", "Restart detected. No pending tasks to resume.")

    def _execute_todos(self, todos: List[Dict], start_index: int = 0, context_msg: str = ""):
        if context_msg:
            self.add_chat("info", context_msg)

        self.remediation.save_state(todos, start_index)
        total = len(todos)

        for i in range(start_index, total):
            todo = todos[i]
            action = todo.get("action", todo.get("action_type", "?"))
            desc = todo.get("description", "Execute step")
            params = todo.get("params", {})
            needs_restart = todo.get("requires_restart", False)

            detail_lines = [f"Step {i+1}/{total}: {desc}"]
            for k, v in params.items():
                detail_lines.append(f"  {k}: {v}")
            detail_str = "\n".join(detail_lines)

            choice = messagebox.askyesnocancel(
                f"Execute Step {i+1}/{total}?",
                f"{detail_str}\n\n"
                f"Yes = Execute this step\n"
                f"No = Skip this step\n"
                f"Cancel = Stop execution"
            )

            if choice is None:
                self.add_chat("info", f"Stopped execution at step {i+1}/{total}.")
                self.remediation.save_state(todos, i)
                return
            elif not choice:
                self.add_chat("info", f"Skipped: {desc}")
                self.remediation.save_state(todos, i + 1)
                continue

            self.add_chat("action", f"Executing: {desc}")
            self.status.set(f"Executing: {desc}")
            result = self.remediation.execute(action, params)

            if result.get("restart"):
                self.add_chat("info", "Restart required. Saving progress...")
                self.remediation.mark_restart_initiated()
                self.remediation.save_state(todos, i + 1)
                self.add_chat("action",
                    "Please restart your PC now. When you reopen this app, "
                    "I'll continue from where I left off.")
                return

            if result.get("success"):
                self.add_chat("solution", f"Success: {result.get('message', desc)}")
            else:
                self.add_chat("finding",
                    f"Failed: {result.get('error', result.get('message', 'Unknown error'))}")
                retry = messagebox.askyesno(
                    "Step Failed",
                    f"Step {i+1} failed: {result.get('error', 'Unknown error')}\n\nTry again?"
                )
                if retry:
                    result = self.remediation.execute(action, params)
                    if result.get("success"):
                        self.add_chat("solution", f"Success on retry: {result.get('message', desc)}")
                    else:
                        self.add_chat("finding", f"Still failed: {result.get('error', 'Unknown error')}")
                        self.add_chat("info", "You can try this step manually.")
                else:
                    self.add_chat("info", "You can try this step manually later.")

            self.add_chat("reasoning", "Verifying result...")
            verify_result = self.remediation.verify(action, params)
            if verify_result.get("success"):
                self.add_chat("solution", f"Verified: {verify_result.get('message', 'OK')}")
            else:
                self.add_chat("finding",
                    f"Verification warning: {verify_result.get('message', 'Could not verify')}")

            self.remediation.save_state(todos, i + 1)
            self.status.set("Ready")

        self.remediation.clear_state()
        self.add_chat("header", "=== All Steps Complete ===")
        self.add_chat("agent", "All action steps have been processed.")
        self.add_chat("info", "If the issue persists, describe it again for further analysis.")

    def display_analysis(self, analysis: Dict):
        """Display analysis results"""
        it = analysis.get('issue_type', 'General')
        self.add_chat("header", f"=== {it} ===")
        self.add_chat("agent", f"Severity: {analysis.get('severity', 'Low')}")

        for r in analysis.get('reasoning', []):
            self.add_chat("reasoning", r)

        llm_answer = analysis.get("llm_answer", "")
        if llm_answer:
            self.add_chat("agent", llm_answer)

        for f in analysis.get('findings', [])[:3]:
            self.add_chat("finding", f)

        for s in analysis.get('recommendations', [])[:6]:
            self.add_chat("solution", s)

        for a in analysis.get('actions', []):
            self.add_chat("action", a.get("label", str(a)))

        steps = analysis.get('next_steps', [])
        if steps:
            self.add_chat("agent", "Next steps:")
            for s in steps[:4]:
                self.add_chat("info", s)

    # ============================================================
    # Provider settings
    # ============================================================

    CONFIG_FILE = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                               "AITroubleshooter", "provider_config.json")

    def load_api_config(self) -> Dict:
        import json as _json
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE) as f:
                    return _json.load(f)
        except:
            pass
        return {"provider": "ollama", "api_key": "", "base_url": "", "model": ""}

    def save_api_config(self, config: Dict):
        import json as _json
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            _json.dump(config, f)
        self.api_config = config

    def apply_provider_config(self, config: Dict):
        provider_name = config.get("provider", "ollama")
        if provider_name == "ollama":
            self.agent_loop.set_providers([OllamaProvider(url=self.agent_loop.ollama_url)])
        else:
            preset = PROVIDER_PRESETS.get(provider_name, {})
            base_url = config.get("base_url") or preset.get("base_url", "https://api.openai.com/v1")
            model = config.get("model") or preset.get("default_model", "gpt-4o-mini")
            api_key = config.get("api_key", "")
            if api_key:
                api_provider = OpenAICompatibleProvider(api_key, base_url, model)
                self.agent_loop.set_providers([api_provider])
                self.agent_loop.model = model
        self.using_llm = self.agent_loop.active_provider is not None
        self.update_mode_label()

    def open_settings(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Provider Settings")
        dialog.geometry("500x520")
        dialog.transient(self)
        dialog.grab_set()

        config = dict(self.api_config)

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="LLM Provider", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(frame, text="Provider:").pack(anchor="w")
        providers = ["ollama"] + list(PROVIDER_PRESETS.keys())
        provider_var = tk.StringVar(value=config.get("provider", "ollama"))
        provider_menu = ctk.CTkOptionMenu(frame, values=providers, variable=provider_var)
        provider_menu.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="API Key:").pack(anchor="w")
        api_key_entry = ctk.CTkEntry(frame, placeholder_text="sk-...", show="*")
        api_key_entry.insert(0, config.get("api_key", ""))
        api_key_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Base URL:").pack(anchor="w")
        base_url_entry = ctk.CTkEntry(frame, placeholder_text="https://api.openai.com/v1")
        base_url_entry.insert(0, config.get("base_url", ""))
        base_url_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Model:").pack(anchor="w")
        model_entry = ctk.CTkEntry(frame, placeholder_text="gpt-4o-mini")
        model_entry.insert(0, config.get("model", ""))
        model_entry.pack(fill="x", pady=(0, 10))

        def on_provider_change(*args):
            pname = provider_var.get()
            if pname == "ollama":
                api_key_entry.delete(0, "end")
                base_url_entry.delete(0, "end")
                model_entry.delete(0, "end")
            elif pname in PROVIDER_PRESETS:
                preset = PROVIDER_PRESETS[pname]
                base_url_entry.delete(0, "end")
                base_url_entry.insert(0, preset["base_url"])
                model_entry.delete(0, "end")
                model_entry.insert(0, preset["default_model"])

        provider_var.trace_add("write", on_provider_change)

        def test_connection():
            pname = provider_var.get()
            key = api_key_entry.get().strip()
            url = base_url_entry.get().strip()
            model = model_entry.get().strip()

            if pname == "ollama":
                ok = self.agent_loop.is_ollama_available()
                messagebox.showinfo("Test", "Ollama is available!" if ok else "Ollama is not running.")
                return

            if not key:
                messagebox.showerror("Error", "API key is required")
                return
            if not url:
                url = PROVIDER_PRESETS.get(pname, {}).get("base_url", "https://api.openai.com/v1")
            if not model:
                model = PROVIDER_PRESETS.get(pname, {}).get("default_model", "gpt-4o-mini")

            self.status.set("Testing API connection...")
            try:
                test_provider = OpenAICompatibleProvider(key, url, model)
                response = test_provider.call([
                    {"role": "user", "content": "Say 'OK' and nothing else."}
                ], model)
                if "OK" in response:
                    messagebox.showinfo("Test", f"Connection works! Response: {response.strip()}")
                else:
                    messagebox.showinfo("Test", f"Connected. Response: {response.strip()}")
            except Exception as e:
                messagebox.showerror("Connection Failed", str(e))
            finally:
                self.status.set("Ready")

        ctk.CTkButton(frame, text="Test Connection", command=test_connection,
                      fg_color="#ffaa00", text_color="#000000"
                      ).pack(fill="x", pady=(5, 15))

        def save():
            config["provider"] = provider_var.get()
            config["api_key"] = api_key_entry.get().strip()
            config["base_url"] = base_url_entry.get().strip()
            config["model"] = model_entry.get().strip()
            self.save_api_config(config)
            self.apply_provider_config(config)
            self.add_chat("info", f"Provider set to: {config['provider']}")
            messagebox.showinfo("Saved", f"Provider configuration saved.\n"
                                         f"Active: {config['provider']}\n"
                                         f"Model: {config.get('model') or 'default'}")
            dialog.destroy()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(btn_frame, text="Save", command=save, fg_color="#00d4ff", text_color="#000000").pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right")

        on_provider_change()

    def execute_defender_scan(self):
        self.add_chat("agent", "Running Windows Defender Quick Scan...")
        self.add_chat("reasoning", "This may take a few minutes...")
        self.status.set("Scanning for malware...")

        def scan():
            try:
                result = self.diagnostics.run_windows_defender_scan()
                if result.get("status") == "completed":
                    self.add_chat("finding", "Defender scan completed - no threats found")
                    self.add_chat("solution", "For thorough check: Windows Security -> Full scan")
                else:
                    self.add_chat("finding", f"Result: {result.get('message', 'Check Windows Security')}")
                self.status.set("Ready")
            except Exception as e:
                self.add_chat("finding", f"Error: {str(e)}")
                self.status.set("Error")
            finally:
                self.send_btn.configure(state="normal")

        thread = threading.Thread(target=scan)
        thread.daemon = True
        thread.start()

    def execute_chkdsk(self):
        self.add_chat("agent", "Checking disk for errors...")
        self.status.set("Checking disk...")

        def check():
            try:
                result = self.diagnostics.run_chkdsk()
                if result.get("has_bad_sectors"):
                    self.add_chat("finding", "WARNING: Bad sectors detected! Backup data immediately!")
                elif result.get("has_errors"):
                    self.add_chat("finding", "Minor file system issues found")
                else:
                    self.add_chat("finding", "Disk check completed - no errors found")
                self.status.set("Ready")
            except Exception as e:
                self.add_chat("finding", f"Error: {str(e)}")
                self.status.set("Error")
            finally:
                self.send_btn.configure(state="normal")

        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()

    def run_diagnostics(self):
        """Run full diagnostics"""
        self.diagnose_btn.configure(state="disabled")
        thread = threading.Thread(target=self._diagnose_thread)
        thread.daemon = True
        thread.start()

    def _diagnose_thread(self):
        """Diagnostics thread"""
        try:
            self.status.set("Running diagnostics...")
            self.current_diagnostics = self.diagnostics.get_system_info()
            self.update_system_display()
            self.status.set("Ready")
        except Exception as e:
            self.add_chat("agent", f"Error: {str(e)}", "finding")
            self.status.set("Error")
        finally:
            self.diagnose_btn.configure(state="normal")

    def update_system_display(self):
        """Update system info display"""
        self.system_info.config(state="normal")
        self.system_info.delete(1.0, "end")

        if not self.current_diagnostics:
            self.system_info.insert("end", "No data\n")
            self.system_info.config(state="disabled")
            return

        d = self.current_diagnostics

        self.system_info.insert("end", "--- CPU ---\n", "header")
        cpu = d.get('cpu', {})
        self.system_info.insert("end", f"Usage: {cpu.get('usage_percent', 0):.1f}%\n")
        self.system_info.insert("end", f"Status: {cpu.get('status', 'N/A')}\n\n")

        self.system_info.insert("end", "--- RAM ---\n", "header")
        mem = d.get('memory', {})
        tag = "critical" if mem.get('percent', 0) > 90 else "warning" if mem.get('percent', 0) > 80 else "good"
        self.system_info.insert("end", f"Used: {mem.get('percent', 0):.1f}%\n", tag)
        self.system_info.insert("end", f"Available: {format_bytes(mem.get('available', 0))}\n\n")

        self.system_info.insert("end", "--- DISK ---\n", "header")
        for p in d.get('disk', {}).get('partitions', [])[:2]:
            tag = "critical" if p.get('percent', 0) > 90 else "warning" if p.get('percent', 0) > 80 else "good"
            self.system_info.insert("end", f"{p['device']}: {p.get('percent', 0):.1f}%\n", tag)

        self.system_info.config(state="disabled")


def main():
    """Main entry point"""
    app = EnhancedTroubleshootingAgent()
    app.mainloop()


if __name__ == "__main__":
    main()
