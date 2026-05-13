// Modal and Envelope Logic
async function openEnvelope(type) {
    try {
        const response = await fetch(`/api/content/${type}`);
        const data = await response.json();
        
        const overlay = document.getElementById('modal-overlay');
        const title = document.getElementById('modal-title');
        const text = document.getElementById('modal-text');
        const icon = document.getElementById('modal-icon');
        const mediaContainer = document.getElementById('audio-container');

        title.innerText = data.title;
        text.innerText = data.text;
        icon.className = `fas ${data.icon}`;
        icon.style.color = data.color;

        // Reset and populate media container
        mediaContainer.innerHTML = '';
        
        if (data.media && data.media.length > 0) {
            data.media.forEach(item => {
                const itemWrapper = document.createElement('div');
                itemWrapper.style.marginBottom = '20px';
                
                if (item.type === 'audio') {
                    const label = document.createElement('div');
                    label.style.fontSize = '0.9rem';
                    label.style.marginBottom = '5px';
                    label.innerText = item.label || 'Голосовое сообщение';
                    
                    const audio = new Audio(item.url);
                    const playBtn = document.createElement('button');
                    playBtn.className = 'btn-hint';
                    playBtn.style.padding = '8px 15px';
                    playBtn.innerHTML = '<i class="fas fa-play"></i> Слушать';
                    
                    playBtn.onclick = () => {
                        audio.play().catch(e => console.log('Playback blocked or failed', e));
                    };
                    
                    itemWrapper.appendChild(label);
                    itemWrapper.appendChild(playBtn);
                } else if (item.type === 'image') {
                    const img = document.createElement('img');
                    img.src = item.url;
                    img.style.maxWidth = '100%';
                    img.style.borderRadius = '15px';
                    img.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                    img.alt = item.label || 'Фото';
                    
                    const label = document.createElement('div');
                    label.style.fontSize = '0.8rem';
                    label.style.marginTop = '5px';
                    label.innerText = item.label || '';
                    
                    itemWrapper.appendChild(img);
                    itemWrapper.appendChild(label);
                }
                
                mediaContainer.appendChild(itemWrapper);
            });
        }

        overlay.classList.add('active');
    } catch (error) {
        console.error('Error fetching envelope content:', error);
    }
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

// Background Effects
function initBackground() {
    const bg = document.getElementById('bg-layer');
    if (!bg) return;
    
    // Create stars
    for (let i = 0; i < 50; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 3 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDelay = `${Math.random() * 5}s`;
        bg.appendChild(star);
    }

    // Create clouds
    const cloudCount = window.innerWidth < 600 ? 3 : 6;
    for (let i = 0; i < cloudCount; i++) {
        createCloud();
    }
}

function createCloud() {
    const bg = document.getElementById('bg-layer');
    const cloud = document.createElement('div');
    cloud.className = 'cloud';
    const width = Math.random() * 150 + 100;
    cloud.style.width = `${width}px`;
    cloud.style.height = `${width * 0.4}px`;
    cloud.style.left = `${Math.random() * 100}%`;
    cloud.style.top = `${Math.random() * 80}%`;
    cloud.style.opacity = Math.random() * 0.4 + 0.4;
    cloud.style.animationDuration = `${Math.random() * 20 + 20}s`;
    cloud.style.animationDelay = `-${Math.random() * 20}s`;
    
    const before = document.createElement('div');
    before.style.cssText = `position:absolute; background:inherit; border-radius:50%; width:${width*0.5}px; height:${width*0.5}px; top:-${width*0.25}px; left:${width*0.15}px;`;
    const after = document.createElement('div');
    after.style.cssText = `position:absolute; background:inherit; border-radius:50%; width:${width*0.6}px; height:${width*0.6}px; top:-${width*0.3}px; right:${width*0.15}px;`;
    
    cloud.appendChild(before);
    cloud.appendChild(after);
    bg.appendChild(cloud);
}

const tips = [
    "Ты сегодня выглядишь просто чудесно! ✨",
    "Не забудь выпить водички и немного отдохнуть 🌸",
    "Я горжусь тобой и всем, что ты делаешь ❤️",
    "Обнимаю тебя крепко-крепко через экран! 🤗",
    "Твоя улыбка освещает весь этот мир 🌟"
];

function showRandomTip() {
    const tip = tips[Math.floor(Math.random() * tips.length)];
    const title = document.getElementById('modal-title');
    const text = document.getElementById('modal-text');
    const icon = document.getElementById('modal-icon');
    const overlay = document.getElementById('modal-overlay');
    const mediaContainer = document.getElementById('audio-container');

    title.innerText = "Маленькое напоминание...";
    text.innerText = tip;
    icon.className = "fas fa-magic";
    icon.style.color = "#ff80ab";
    mediaContainer.innerHTML = '';
    
    overlay.classList.add('active');
}

// Check for character images and replace SVGs if they exist
function checkCharacterImages() {
    const characters = {
        'chiikawa': 'chiikawa.png',
        'hachiware': 'hachiware.png',
        'chopper': 'chopper.png',
        'usagi': 'usagi.png',
        'perun': 'perun.png',
        'going-merry': 'merry.png'
    };

    Object.keys(characters).forEach(key => {
        const className = key;
        const filename = characters[key];
        const el = document.querySelector(`.${className}`);
        if (!el) return;

        const imgPath = `/static/assets/images/${filename}`;
        
        // Try to load the image
        const img = new Image();
        img.onload = function() {
            // If image loads, clear the SVG and set background or append img
            el.innerHTML = '';
            el.style.backgroundImage = `url('${imgPath}')`;
            el.style.backgroundSize = 'contain';
            el.style.backgroundRepeat = 'no-repeat';
            el.style.backgroundPosition = 'center';
            // Adjust dimensions if needed
            el.style.height = el.offsetWidth + 'px'; 
        };
        img.src = imgPath;
    });
}

// Close modal on click outside
window.onclick = function(event) {
    const overlay = document.getElementById('modal-overlay');
    if (event.target == overlay) {
        closeModal();
    }
}

// Init
window.onload = () => {
    initBackground();
    checkCharacterImages();
};
