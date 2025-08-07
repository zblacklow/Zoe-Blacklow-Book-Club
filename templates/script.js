    document.addEventListener('DOMContentLoaded', () => {
      const stars = document.querySelectorAll('.star');
      const ratingText = document.getElementById('rating-text');

      stars.forEach(star => {
        star.addEventListener('click', async () => {
          const rating = star.getAttribute('data-value');

          stars.forEach(s => s.classList.remove('selected'));
          for (let i = 0; i < rating; i++) {
            stars[i].classList.add('selected');
          }

          ratingText.textContent = `You rated this ${rating} star(s).`;

          await fetch('/submit-rating', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rating: parseInt(rating) }),
          });
        });
      });
    });