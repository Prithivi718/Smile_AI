$(document).ready(function () {
    try {
        // Textillate Example Animation
        $('#textillateExample').textillate({
            loop: true,
            sync: true,
            in: { effect: 'bounceIn' },
            out: { effect: 'bounceOut' }
        });
    }
}
