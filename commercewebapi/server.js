const express = require("express");
const fileUpload = require("express-fileupload");
const porn_filter = require("./porn_filter");

const app = express();
// TODO(jan): For local machine
const port = 8001;

app.use(fileUpload());

// TODO(jan): Production should be process.env.PORT cus of Heroku
const server = app.listen(process.env.PORT, () => {
  console.log(`Listening at -> http://localhost:${server.address().port}`);
});

app.post("/upload", function (req, res) {
  let sampleFile;
  let uploadPath;

  if (!req.files || Object.keys(req.files).length === 0) {
    return res.status(400).send("No files were uploaded.");
  }

  sampleFile = req.files.sampleFile;
  uploadPath = __dirname + "/saved.png";

  sampleFile.mv(uploadPath, async function (err) {
    if (err) return res.status(500).send(err);

    if (sampleFile.mimetype === "image/png") {
      const result = await porn_filter.fn();
      res.send(`${result}`);
    } else {
      res.send(`Not an image.png`);
    }
  });
});
