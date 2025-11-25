// ========================
// SMOOTH SCROLL FOR NAV LINKS
// ========================
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// ========================
// CONTACT FORM FUNCTIONALITY
// ========================
const form = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');

if(form){
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            name: form.name.value.trim(),
            email: form.email.value.trim(),
            message: form.message.value.trim()
        };

        if(!formData.name || !formData.email || !formData.message){
            formStatus.textContent = 'Please fill all fields ❌';
            formStatus.style.color = 'red';
            return;
        }

        try {
            formStatus.textContent = 'Sending message... ⏳';
            formStatus.style.color = '#2E8B57';

            const response = await fetch('/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if(result.status === 'success'){
                formStatus.textContent = 'Message sent successfully! ✅';
                formStatus.style.color = 'green';
                form.reset();
            } else {
                formStatus.textContent = 'Error sending message ❌';
                formStatus.style.color = 'red';
            }
        } catch(err){
            formStatus.textContent = 'Error sending message ❌';
            formStatus.style.color = 'red';
        }
    });
}

// ========================
// SCROLL ANIMATION FOR SECTIONS
// ========================
const sections = document.querySelectorAll('.section');

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if(entry.isIntersecting){
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.2 });

sections.forEach(section => observer.observe(section));

// ========================
// PORTFOLIO FILTER FUNCTIONALITY
// ========================
const portfolioCards = document.querySelectorAll('.portfolio-list .card');

function filterPortfolio(category){
    portfolioCards.forEach(card => {
        if(category === 'all' || card.textContent.toLowerCase().includes(category)){
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Optional: Add filter buttons dynamically
// Example: <button onclick="filterPortfolio('web')">Web Development</button>

// ========================
// STUDENT SUPPORT CENTER TABS FUNCTIONALITY
// ========================
const supportTabs = document.querySelectorAll('.support-tab');
const supportContents = document.querySelectorAll('.support-content');

supportTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        supportTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const target = tab.dataset.target;
        supportContents.forEach(content => {
            content.style.display = content.id === target ? 'block' : 'none';
        });
    });
});

// ========================
// OPTIONAL: BACK TO TOP BUTTON
// ========================
const backTop = document.createElement('button');
backTop.textContent = '⬆';
backTop.style.cssText = `
position: fixed; bottom: 20px; right: 20px; 
padding: 10px 15px; background: #2E8B57; color: #fff; 
border: none; border-radius: 50%; font-size: 20px; cursor: pointer; display: none; z-index: 1000;
`;
document.body.appendChild(backTop);

backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

window.addEventListener('scroll', () => {
    backTop.style.display = window.scrollY > 300 ? 'block' : 'none';
});

// ========================
// ADD ANIMATION CLASS FOR CSS
// ========================
sections.forEach(section => {
    section.classList.add('section-hidden'); // Initially hidden
});

