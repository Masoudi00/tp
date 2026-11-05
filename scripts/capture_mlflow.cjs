// Capture the actual local MLflow UI using an isolated headless browser.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const page = await browser.newPage({viewport: {width: 1600, height: 1800}});
  await page.goto('http://127.0.0.1:5000', {waitUntil: 'domcontentloaded'});
  await page.getByText('Model training', {exact: true}).click();
  await page.getByText('TP_Iris_Classification', {exact: true}).first().click();
  await page.getByText('random_forest_Iris', {exact: true}).first().waitFor();
  await page.screenshot({path: 'reports/mlflow-experiments.png', fullPage: true});
  await page.getByText('random_forest_Iris', {exact: true}).first().click();
  await page.getByText('0.9', {exact: true}).first().waitFor();
  await page.screenshot({path: 'reports/mlflow-random-forest.png', fullPage: true});
  fs.writeFileSync('reports/mlflow-ui-location.txt', page.url() + '\n');
  await browser.close();
})();
