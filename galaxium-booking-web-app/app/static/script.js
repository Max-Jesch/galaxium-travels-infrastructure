document.addEventListener('DOMContentLoaded', function() {
    // Book flight functionality
    document.querySelectorAll('.book-btn').forEach(button => {
        button.addEventListener('click', function() {
            const flightId = this.getAttribute('data-flight-id');

            fetch('/book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `flight_id=${flightId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(`Flight booked successfully! Booking ID: ${data.booking_id}`);
                    window.location.href = '/bookings';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while booking the flight');
            });
        });
    });

    // Cancel booking functionality
    document.querySelectorAll('.cancel-btn').forEach(button => {
        button.addEventListener('click', function() {
            const bookingId = this.getAttribute('data-booking-id');

            if (confirm('Are you sure you want to cancel this booking?')) {
                fetch(`/cancel/${bookingId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        alert('Booking cancelled successfully!');
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while cancelling the booking');
                });
            }
        });
    });
});