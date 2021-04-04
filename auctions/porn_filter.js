// Credit: https://github.com/infinitered/nsfwjs#node-js-app
const axios = require('axios')
const tf = require('@tensorflow/tfjs-node')
const fs = require('fs')
const nsfw = require('nsfwjs')
async function fn() {
  const pic = await fs.promises.readFile('./saved_image.jpg', {
    responseType: 'arraybuffer',
  })
  const model = await nsfw.load()
  const image = await tf.node.decodeImage(pic,3)
  const predictions = await model.classify(image)
  image.dispose()

  function checking() {
    for (let {className, probability} of predictions) {
      if (className === "Porn" || className === "Hentai" || className === "Sexy") {
        if (probability >= 0.5) {
          return "Not allow";
        }
      }
    }
    return "Allow";
  }
  const result = checking()
  console.log(result)
}
fn()
