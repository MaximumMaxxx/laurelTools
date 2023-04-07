let markdownit = require('markdown-it');
let hljs = require('highlight.js');
let math_plugin = require('markdown-it-mathjax3');

const md = markdownit({
    highlight: (
        str,
        lang,
    ) => {
    const code = lang && hljs.getLanguage(lang)
        ? hljs.highlight(str, {
            language: lang,
            ignoreIllegals: true,
        }).value
            : md.utils.escapeHtml(str);
        return `<pre class="hljs"><code>${code}</code></pre>`;
        },
    });
md.use(math_plugin);


let messages = []

window.handleSubmit = function (e) {
    handleSubmit(e);
}

        function createMessage(message = messages[messages.length - 1]) {
            let p = document.createElement('p')

            let parsedMessage = md.render(message.content)
            if (message.role === 'user') {
                p.classList.add('userMsg')
                p.innerHTML = parsedMessage
            } else {
                p.classList.add('gptResponse')
                p.innerHTML = parsedMessage
            }
            document.querySelector('#conversation').appendChild(p)
        }

        // Handle the form submission
        function handleSubmit(e) {
            e.preventDefault()
            // Get the user prompt
            let userPrompt = document.querySelector('textarea[name="userPrompt"]').value
            document.querySelector('textarea[name="userPrompt"]').value = ''
            // Get the system prompt
            let systemPrompt = document.querySelector('#prompt').innerText
            // turn the messages array into a string
            let messagesString = JSON.stringify(messages)
            // Grab the submit button
            let submitButton = document.querySelector('#chat-submit')
            messages.push({
                role: 'user',
                content: userPrompt
            })
            createMessage()
            // Make a POST request to the server
            fetch('/chat/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userPrompt: userPrompt,
                    systemPrompt: systemPrompt,
                    messages: messagesString
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                // Update the messages
                messages.push(data)
                createMessage();
                // Clear the user prompt
            })
            .catch(error => {
                console.error('Error:', error)
            })

        }