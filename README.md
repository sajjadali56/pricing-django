# Pricing Django Based

Pricing Django-Based Application


## 🚀 Running the Project – Step-by-Step Guide

### ✅ Prerequisites:

* Ensure **Python** is installed.
* Confirm that the project contains a `Pipfile`.
n

---

### 🧭 Step 1: Navigate to the Project Folder

1. Open the folder where your code/project is located (e.g., `EOS`).
2. Click on the **address bar** at the top (where the path is displayed).
3. Clear the path by pressing `Backspace`, then type: `cmd`
4. Press `Enter`. A **Command Prompt** window will open in that folder.

---

### 🧪 Step 2: Check Python Version

In the Command Prompt, type the following and press `Enter`:

```sh
python --version
```

✅ You should see an output similar to:

```sh
Python 3.10.6
```

---

### 🧾 Step 3: Match Python Version in `Pipfile`

1. Open the `Pipfile` (located in the same folder).
2. Look for a line like:

```sh
[requires]
python_version = "3.10"
```

3. Make sure the Python version in the `Pipfile` matches the version you saw in the terminal (`python --version`).

   * If they are different, update the `python_version` value in the `Pipfile` accordingly.

---

### ⚙️ Step 4: Install and Run the App

Run the following commands **one by one** in the same Command Prompt window:

```sh
python -m pip install pipenv
pipenv shell
pipenv install
python manage.py migrate
python manage.py runserver
```

### ⚠️ `pipenv` Not Working?

Sometimes, after installing `pipenv`, you may run into an error like:

```sh
'pipenv' is not recognized as an internal or external command, operable program or batch file.
```

This usually means the system can’t find the `pipenv` executable because it’s not added to your system’s **Environment Variables**.

---

#### 🛠 Step-by-Step Instructions

---

#### 🔹 Step A: Locate Your Pipenv Installation Path

1. First, run the following command to find where `pipenv` is installed:

   ```sh
   pip show pipenv
   ```

2. Look for the line that starts with `Location:`
   For example:

   ```sh
   Location: C:\Users\YourUsername\AppData\Roaming\Python\Python310\Scripts
   ```

3. That folder (ending in `Scripts`) contains `pipenv.exe`. Copy this path.

---

#### 🔹 Step B: Add That Folder to Environment Variables

1. Press `Win + S` and search for **“Environment Variables”**.
2. Click **“Edit the system environment variables”**.
3. In the System Properties window, click on the **“Environment Variables…”** button.
4. Under **User variables**, find and select the variable named **`Path`**, then click **Edit**.
5. Click **New** and **paste** the path you copied in Step 1.
6. Click **OK** on all open windows to save and exit.

---

#### 🔹 Step C: Restart the Terminal

1. Close all open Command Prompt, PowerShell, or VS Code Terminal windows.
2. Open a new Command Prompt using the `step 1` instructions provided above.
3. Type:

   ```sh
   pipenv --version
   ```

   ✅ You should now see something like:

   ```sh
   pipenv, version 2023.x.x
   ```

---

#### 🧪 Still Not Working?

If `pipenv` still doesn't work:

1. Try installing it again using:

```sh
pip install --user pipenv
```

2. Repeat `Step A` and make sure the new `Scripts` path is added to `Path`.

---

#### 🟢 That’s it! You’ve successfully configured `pipenv` on your system.

You can now run by `Step 4` by executing the next three commands!

---

### 🟢 That’s it! You should now see your app running in your browser.

If you face any issues or errors during these steps, share the error message for troubleshooting.

### 📝 Additional Notes

- `Steps 2,3 and 4` are required only for the first run!
- If already set it up, then just run:

```sh
pipenv shell
python manage.py runserver
```

## Create Superuser

Run the following command

```sh
python manage.py createsuperuser
```

After running the above command, you will be redirected to the login page! You can create the super user here
