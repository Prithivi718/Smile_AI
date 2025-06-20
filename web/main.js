$(document).ready(function () {
    try {
        // Textillate Example Animation
        $('#textillateExample').textillate({
            loop: true,
            sync: true,
            in: { effect: 'bounceIn' },
            out: { effect: 'bounceOut' }
        });

        // Typing effect
        // $('.chat-messages').textillate({
        //     loop: true,
        //     sync: true,
        //     in: { effect: 'pulse', sync: true },
        //     out: { effect: 'pulse', sync: true }
        // });

        // ChatBox functionality
        function ChatBox(message) {
            try {
                if (message !== "") {
                    $("#textillateExample").attr("hidden", true);
                    $("#chat-interface").attr("hidden", false);
                    eel.chain_start(message)(async function (ret) {
                        const { tool, content } = ret || {};

                        if (tool === "youtubeagent") {
                            renderYouTubeResults(content);
                        }
                        else if (tool === "chatcompanion") {
                            renderChatMessage(content);
                        }
                        else {
                            // Fallback to plain chat
                            renderChatMessage(content || String(ret));
                        }
                    });
                    $("#chatbox").val("");
                    $("#micbtn").attr('hidden', false);
                    $("#sendbtn").attr('hidden', true);
                }
            } catch (error) {
                console.error("Error handling chat box message:", error.message);
            }
        }

        // Toggle mic and send buttons based on message input
        function ShowHideButton(message) {
            try {
                if (message.length === 0) {
                    $("#micbtn").attr('hidden', false);
                    $("#sendbtn").attr('hidden', true);
                } else {
                    $("#micbtn").attr('hidden', true);
                    $("#sendbtn").attr('hidden', false);
                }
            } catch (error) {
                console.error("Error toggling buttons:", error.message);
            }
        }

        // Key up event handler for chat box
        $("#chatbox").keyup(function () {
            try {
                let message = $("#chatbox").val();
                ShowHideButton(message);
            } catch (error) {
                console.error("Error handling keyup event:", error.message);
            }
        });

        // Send button click handler
        $("#sendbtn").click(function () {
            try {
                let message = $("#chatbox").val();
                ChatBox(message);
            } catch (error) {
                console.error("Error handling send button click:", error.message);
            }
        });

        // Enter key press event handler for chat box
        $("#chatbox").keypress(function (e) {
            try {
                if (e.which === 13) {
                    let message = $("#chatbox").val();
                    ChatBox(message);
                }
            } catch (error) {
                console.error("Error handling enter key press:", error.message);
            }
        });


        //  Chat Bot Response handler (returns HTMLDivElement, like renderYouTubeResults)
        function renderChatMessage(content) {
            try {
                if (!content) return;

                // 🧠 Basic Markdown Parser
                const parseMarkdown = (text) => {
                    return text
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')     // Bold
                        .replace(/_(.*?)_/g, '<em>$1</em>')                   // Italic
                        .replace(/`([^`]+)`/g, '<code>$1</code>')             // Inline Code
                        .replace(/\n/g, '<br>')                               // Line breaks
                        .replace(/https?:\/\/[^\s]+/g, function (url) {       // Links
                            return `<a href="${url}" target="_blank">${url}</a>`;
                        });
                };

                const formattedMessage = parseMarkdown(content);
        
                // 👇 Inject it using your controller
                if (typeof window.addAssistantMessage === "function") {
                    window.addAssistantMessage(formattedMessage);
                } else {
                    console.warn("window.addAssistantMessage is not defined.");
                    // Optional fallback if addAssistantMessage is not defined

                    const chatMessages = document.getElementById("chat-messages");
                    const msg = document.createElement("div");
                    msg.innerHTML = formatted;
                    chatMessages.appendChild(msg);
                }

            } catch (error) {
                console.error("Error rendering AI message:", error.message);
            }
        }
        



        // Youtube Logic Handling for Videos Show-UP
        function renderYouTubeResults(videos) {
            // videos: Array of { title, description, embed_url }
            if (!Array.isArray(videos)) {
                // fallback
                return renderChatMessage(String(videos));
            }

            videos.forEach((video, idx) => {
                const html = `
                <div class="video-box mb-3 p-2 border rounded" id="video-box-${idx}">
                  <div class="video-title fw-bold mb-1" id="video-title-${idx}" style="cursor:pointer;">
                    ${video.title}
                  </div>
                  <div class="video-desc mt-2 ps-3" id="video-desc-${idx}" style="display:none;">
                    ${video.description}
                    <div class="mt-2">
                      <iframe width="300" height="200"
                              src="${video.embed_url}"
                              frameborder="0" allowfullscreen>
                      </iframe>
                    </div>
                  </div>
                </div>
              `;
                window.addAssistantMessage(html);

                // Attach toggle handler
                setTimeout(() => {
                    const header = document.getElementById(`video-title-${idx}`);
                    const desc = document.getElementById(`video-desc-${idx}`);
                    if (desc) {
                        desc.style.display = 'block';
                    }
                }, 0);
            });
        }




        // 1) Fetch notifications from Python via Eel
        async function fetchNotifications() {
            try {
                // This actually invokes the Python function and returns the real result
                const notifs = await eel.get_notifications()();

                console.log("Debug: raw notifications from Python:", notifs);

                // If Python returned a single object instead of an Array, wrap it
                if (notifs && !Array.isArray(notifs)) {
                    console.warn("Expected array but got:", notifs);
                    return [notifs];
                }
                return Array.isArray(notifs) ? notifs : [];
            } catch (err) {
                console.error("Failed to fetch notifications:", err);
                return [];
            }
        }

        // 2) Render the boxes given an array of { username, message }
        function renderNotifications(notifications) {
            const container = document.getElementById("notify-container");
            if (!container) {
                console.error("Notification container not found!");
                return;
            }

            // Clear previous entries
            container.innerHTML = "";

            // If empty, show a friendly message
            if (!notifications.length) {
                container.innerHTML = `
                        <div class="notif-box empty-message">
                            No notifications yet
                        </div>`;
                return;
            }

            notifications.forEach(({ username, message }, idx) => {
                // 1) Append new box HTML
                container.innerHTML += `
                    <div class="notif-box mb-3 p-2 border rounded" id="notif-box-${idx}">
                        <div class="notif-username fw-bold mb-1" id="notif-username-${idx}" style="cursor:pointer;">
                            @${username}
                        </div>
                        <div class="notif-message mt-2 ps-3" id="notif-message-${idx}" style="display:none;">
                            ${message}
                        </div>
                    </div>
                `;
            });

            // 2. Attach individual click handlers
            notifications.forEach((_, idx) => {
                const header = document.getElementById(`notif-username-${idx}`);
                const msgBody = document.getElementById(`notif-message-${idx}`);
                const box = document.getElementById(`notif-box-${idx}`);

                header.addEventListener('click', () => {
                    const isHidden = msgBody.style.display === 'none';
                    msgBody.style.display = isHidden ? 'block' : 'none';
                    box.classList.toggle('open', isHidden);
                });
            });
        }



        // When the user clicks the bell/sidebar button
        $("#chat-sidebar-btn").click(async function () {
            try {
                // 1) Fetch the notifications
                const notifications = await fetchNotifications();
                console.log(`Debug: loaded ${notifications.length} notifications`);

                // 2) Render them into the sidebar
                renderNotifications(notifications);
            } catch (error) {
                console.error("Error loading notifications:", error);
                const container = document.getElementById("notify-container");
                if (container) {
                    container.innerHTML = `
                        <div class="notif-box text-danger">
                            Error loading notifications
                        </div>`;
                }
            }
        });
    } catch (error) {
        console.error("Error in document ready:", error);
    }
});