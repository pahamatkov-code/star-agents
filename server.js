const express = require("express");
const multer = require("multer");
const nodemailer = require("nodemailer");
const path = require("path");

const app = express();
const upload = multer();

// Роздача статичних файлів (щоб index.html відкривався з http://localhost:3000)
app.use(express.static(path.join(__dirname, "static")));

// SMTP‑транспортер (налаштуй під свій поштовий сервіс)
const transporter = nodemailer.createTransport({
  host: "smtp.gmail.com",
  port: 587,
  secure: false,
  auth: {
    user: "pahamatkov@gmail.com",
    pass: "mlai vpxs dqdh karj" // Використай App Password
  }
});

// Маршрут прийому PDF і відправки на email
app.post("/send-report", upload.single("file"), async (req, res) => {
  try {
    const mailOptions = {
      from: "your_email@gmail.com",
      to: "recipient@example.com",
      subject: "Star Agents - Автоматичний звіт",
      text: "Додаємо PDF‑звіт із метриками та графіками.",
      attachments: [
        {
          filename: req.file.originalname,
          content: req.file.buffer
        }
      ]
    };

    await transporter.sendMail(mailOptions);
    res.send("Звіт відправлено!");
  } catch (err) {
    console.error(err);
    res.status(500).send("Помилка відправки звіту");
  }
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
