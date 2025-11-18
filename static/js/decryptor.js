(function () {
    "use strict";

    const decoder = new TextDecoder();

    function base64ToBytes(value) {
        const binaryString = globalThis.atob(value);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i += 1) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes;
    }

    async function decryptPayload(ciphertext, iv, key) {
        const cryptoKey = await globalThis.crypto.subtle.importKey(
            "raw",
            key,
            { name: "AES-GCM" },
            false,
            ["decrypt"],
        );
        const buffer = await globalThis.crypto.subtle.decrypt(
            { name: "AES-GCM", iv },
            cryptoKey,
            ciphertext,
        );
        return decoder.decode(buffer);
    }

    async function hydrate() {
        const root = document.getElementById("encrypted-root");
        if (!root) {
            return;
        }

        // Check for Web Crypto API support
        if (!globalThis.crypto || !globalThis.crypto.subtle) {
            console.error("Web Crypto API not supported");
            document.body.classList.add("encryption-error");
            root.hidden = false;
            root.innerHTML = `
                <p>Şifreli içerik çözümlenemedi. Tarayıcınız şifreleme özelliklerini desteklemiyor.</p>
                <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #2c6fff; color: white; border: none; border-radius: 4px; cursor: pointer;">Sayfayı Yenile</button>
            `;
            return;
        }

        try {
            const html = await decryptPayload(
                base64ToBytes(root.dataset.ciphertext || ""),
                base64ToBytes(root.dataset.iv || ""),
                base64ToBytes(root.dataset.key || ""),
            );
            document.body.classList.remove("is-encrypted");
            document.documentElement.classList.add("is-decrypted");
            document.open(root.dataset.mime || "text/html");
            document.write(html);
            document.close();
        } catch (error) {
            console.error("Encrypted payload could not be decrypted", error);
            document.body.classList.add("encryption-error");
            root.hidden = false;
            root.innerHTML = `
                <p>Şifreli içerik çözümlenemedi. Lütfen sayfayı yenileyin.</p>
                <p style="font-size: 0.875rem; color: rgba(29, 53, 87, 0.75); margin-top: 0.5rem;">Hata detayı: ${error.message || 'Bilinmeyen hata'}</p>
                <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #2c6fff; color: white; border: none; border-radius: 4px; cursor: pointer;">Sayfayı Yenile</button>
            `;
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", hydrate, { once: true });
    } else {
        void hydrate();
    }
})();
