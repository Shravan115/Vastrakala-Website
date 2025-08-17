// Cart functionality
let cartCount = 0;
const cartCountSpan = document.getElementById('cart-count');
const cartBadge = document.getElementById('cart-badge');

function updateCart() {
  cartCount++;
  cartCountSpan.textContent = cartCount;
  if (cartBadge) {
    cartBadge.classList.add('active');
    setTimeout(() => cartBadge.classList.remove('active'), 1200);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Hamburger menu
  const hamburger = document.getElementById('hamburger-menu');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
    // Close menu on link click (mobile)
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // Add to Cart buttons
  document.querySelectorAll('.add-cart').forEach(btn => {
    btn.addEventListener('click', updateCart);
  });

  // Smooth scroll for nav links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Fade-in animation on scroll
  const fadeEls = document.querySelectorAll('.fade-in');
  const fadeInOnScroll = () => {
    fadeEls.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 60) {
        el.classList.add('visible');
      }
    });
  };
  window.addEventListener('scroll', fadeInOnScroll);
  fadeInOnScroll();

  // Prevent contact form reload and add validation
  const contactForm = document.querySelector('.contact-form');
  const formError = document.getElementById('form-error');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const name = contactForm.querySelector('input[type="text"]').value.trim();
      const email = contactForm.querySelector('input[type="email"]').value.trim();
      const message = contactForm.querySelector('textarea').value.trim();
      let errorMsg = '';
      if (!name) errorMsg = 'Please enter your name.';
      else if (!email || !/^\S+@\S+\.\S+$/.test(email)) errorMsg = 'Please enter a valid email.';
      else if (!message) errorMsg = 'Please enter your message.';
      if (errorMsg) {
        formError.textContent = errorMsg;
        formError.style.display = 'block';
        return;
      }
      formError.style.display = 'none';
      alert('Thank you for contacting us!');
      contactForm.reset();
    });
  }

  // Category Filter Functionality
  const categoryBtns = document.querySelectorAll('.category-btn');
  const productCards = document.querySelectorAll('.product-card');
  
  if (categoryBtns.length > 0 && productCards.length > 0) {
    categoryBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const category = this.getAttribute('data-category');
        
        // Remove active class from all buttons
        categoryBtns.forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        this.classList.add('active');
        
        // Filter products
        productCards.forEach(card => {
          const cardCategory = card.getAttribute('data-category');
          
          if (category === 'all' || cardCategory === category) {
            card.classList.remove('hidden');
            card.classList.add('visible');
          } else {
            card.classList.add('hidden');
            card.classList.remove('visible');
          }
        });
      });
    });
  }
});
