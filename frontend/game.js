let sessionId = null;

// Create session when page loads
fetch("http://localhost:8000/create-session")
.then(res => res.json())
.then(data => { sessionId = data.session_id; console.log("Session:", sessionId); });

// Upload notes
document.getElementById("uploadBtn").onclick = async () => {
    const file = document.getElementById("fileUpload").files[0];
    if (!file) return alert("Select a file");
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`http://localhost:8000/upload/${sessionId}`, {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    alert(data.status);
};

// Phaser.js Game
document.getElementById("startGameBtn").onclick = () => {
    const config = {
        type: Phaser.AUTO,
        width: 800,
        height: 400,
        parent: "gameContainer",
        scene: {
            preload: preload,
            create: create,
            update: update
        }
    };
    new Phaser.Game(config);
};

let player, cursors, questionText, options = [];

function preload() {
    this.load.image('player', 'https://i.imgur.com/T5uQX6P.png');
}

function create() {
    player = this.add.sprite(100, 300, 'player').setScale(0.5);
    cursors = this.input.keyboard.createCursorKeys();
    loadQuestion(this);
}

function update() {
    if (cursors.left.isDown) player.x -= 5;
    if (cursors.right.isDown) player.x += 5;
    if (cursors.up.isDown) player.y -= 5;
    if (cursors.down.isDown) player.y += 5;
}

// Load question from backend
function loadQuestion(scene) {
    fetch(`http://localhost:8000/question/${sessionId}`)
    .then(res => res.json())
    .then(data => {
        if (data.error) return alert(data.error);
        questionText = scene.add.text(300, 50, data.question, { fontSize: '16px', fill: '#000' });
        options = [];
        data.options.forEach((opt, i) => {
            let btn = scene.add.text(300, 100 + i*30, opt, { fontSize: '14px', backgroundColor: '#ccc' })
                .setInteractive()
                .on('pointerdown', () => {
                    if (i === 0) { alert("Correct! Continue"); loadQuestion(scene); }
                    else { alert("Wrong! Restart"); scene.scene.restart(); }
                });
            options.push(btn);
        });
    });
}
