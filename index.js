function addChatScroll() {
  var chatbot = document.querySelector("#chatbot .bubble-wrap");
  if (chatbot) {
    console.log(chatbot);
    function scrollChatToBottom() {
      console.log("scroll");
      chatbot.scrollTop = chatbot.scrollHeight;
    }
    new MutationObserver(scrollChatToBottom).observe(chatbot, {
      attributes: true,
      childList: true,
      subtree: true,
    });
  } else {
    console.log("retrying");
    setTimeout(addChatScroll, 1000);
  }
}

document.addEventListener("DOMContentLoaded", addChatScroll);
