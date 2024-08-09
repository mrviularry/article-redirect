// Function to set a verification cookie
function setVerificationCookie() {
    var expiryDate = new Date();
    expiryDate.setTime(expiryDate.getTime() + (5 * 60 * 1000)); // 5 minutes expiry
    document.cookie = "js_verified=true; expires=" + expiryDate.toUTCString() + "; path=/";
}

// Function to check the verification cookie
function isVerified() {
    var name = "js_verified=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length) === "true";
        }
    }
    return false;
}

// Set the verification cookie when JavaScript is executed
setVerificationCookie();

// Redirect based on verification status
window.onload = function() {
    if (isVerified()) {
        window.location.href = "main_content.html"; // URL to your main content page
    } else {
        window.location.href = "safe_content.html"; // URL to your error page
    }
}
