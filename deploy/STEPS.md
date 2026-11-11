# Putting the app on AWS for the science fair

A temporary web copy of the app, for 8–11 November. The laptop version (`start.bat`) stays the backup and is not changed by any of this.

**What you get:** `https://mysignlang.duckdns.org`. The team types the shared login once on the Android tablet, and then visitors just use the app. Resetting the statistics needs the reset PIN.

**What gets created:** one CloudFormation stack in Mumbai, with every resource tagged `Project = sign_project`:

- a `c7i.2xlarge` Ubuntu server with a 30 GB disk;
- a fixed IP address;
- a firewall;
- a login key;
- an idle-stop alarm with email;
- a budget alert;
- a private S3 bucket for the webcam photos, in one folder per day (for example `20261110/`) with `success/`, `failure/` and `unknown/` inside, with a permission that lets only the server write to it.

Deleting the stack deletes all of it.

**Cost:** roughly US$28 if the server runs nonstop from Monday to Wednesday evening. It's less if you stop it after school on the 10th. This is an estimate, so check the AWS pricing calculator.

---

## Before you start (once)

In the AWS console, switch the region (top right) to **Asia Pacific (Mumbai)**, then check two things:

1. **Server limit.**
   1. Go to **Service Quotas**, then **Amazon EC2**.
   2. Find **Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances**.
   3. It must be **at least 8**, plus any servers you already run in Mumbai. If it's lower, click **Request increase**.
2. **Default network.** Go to **VPC**, then **Your VPCs**. One row must show **Default VPC: Yes**.

## Step 1: Claim the DuckDNS name

1. Go to https://www.duckdns.org and sign in with Google or GitHub.
2. Type `mysignlang` in the sub domain box and click **add domain**. If you ever use a different name, change `set SERVER=` at the top of `deploy\upload.bat` and `deploy\download_stats.bat`; `upload.bat` then tells the server the new name.
3. Leave the IP address for now. It gets filled in at step 4.

## Step 2: Find your home IP address

From home, open https://checkip.amazonaws.com and write down the number, for example `49.37.10.20`. Only this address will be allowed to copy files to the server.

## Step 3: Create the stack (about 5 minutes)

1. In the AWS console (still in Mumbai), go to **CloudFormation**, then **Create stack**, then **With new resources (standard)**.
2. Choose **Upload a template file**, pick `deploy\cloudformation.yaml`, and click **Next**.
3. **Stack name:** `signlang`. Then fill in the settings:

   | Setting | What to type |
   |---|---|
   | DuckDnsName | `mysignlang` (without `.duckdns.org`) |
   | LoginUser | The shared login name, for example `team` |
   | LoginPassword | The shared password: 8–30 letters and digits, no spaces or symbols |
   | ResetPin | The reset PIN: 4–8 digits |
   | AlertEmail | Your email |
   | HomeIp | The number from step 2 |
   | InstanceType | Leave `c7i.2xlarge` |
   | BudgetUsd | Leave `50`. If this account already spends money on other things this month, make it higher, or the alert will go off straight away. |

4. Click **Next**. Under **Tags**, add **Key** `Project`, **Value** `sign_project`. Click **Next**. At the bottom, tick **I acknowledge that AWS CloudFormation might create IAM resources**. This is the permission for the server to save photos to its own bucket. Then click **Submit**.
5. Wait until the status says **CREATE_COMPLETE**, which takes about 3–5 minutes.
6. Check your email. Open the **AWS Notification – Subscription Confirmation** message and click **Confirm subscription**.

**Already created the stack before the S3 photo storage was added?** Update it instead of making a new one:

1. Go to **CloudFormation**, then **signlang**, then **Update**, then **Replace current template**, and upload the new `deploy\cloudformation.yaml`.
2. On the settings page, keep every setting as it is, then click **Next**.
3. Tick the IAM box, then click **Submit**.
4. When it says **UPDATE_COMPLETE**, run `deploy\upload.bat` again.

## Step 4: Point DuckDNS at the server

1. In the stack, open the **Outputs** tab and copy **FixedIpAddress**.
2. On duckdns.org, paste it into the **current ip** box next to `mysignlang` and click **update ip**.
3. To check: in a command prompt, `nslookup mysignlang.duckdns.org` should show that IP. This can take a minute.

## Step 5: Download the login key

1. In the stack's **Outputs**, copy **KeyParameter**. It looks like `/ec2/keypair/key-0abc...`.
2. Click the **CloudShell** icon (`>_`) in the top bar of the AWS console. When it's ready, type the following, with your KeyParameter in place of `KEY_PARAMETER`:

   ```bash
   aws ssm get-parameter --name KEY_PARAMETER --with-decryption --query Parameter.Value --output text > signlang-key.pem
   ```

3. In CloudShell, click **Actions**, then **Download file**, type `signlang-key.pem`, and click **Download**.
4. Move the downloaded file into the project's `deploy` folder, so it's `deploy\signlang-key.pem`.

**Keep this file private.** Don't email it or put it on a USB stick. `upload.bat` never copies it to the server.

## Step 6: Copy the app to the server (about 10 minutes)

Double-click `deploy\upload.bat`. It packs the app, copies it to the server, installs everything, downloads the AI model, and starts the app. It ends with **All done**.

If you change any code later, run `upload.bat` again. It keeps the statistics already on the server.

## Step 7: Test on the Android tablet

1. On the tablet, in **Chrome**, open `https://mysignlang.duckdns.org`.
2. Type the login. When Chrome offers to save the password, say **Save**.
3. Click **CLICK TO START**. Allow the camera, and choose to allow it every time if Chrome asks.
4. Show a sign and press **Capture**.
5. Open the **(i)** popup and tap **Reset statistics**. It asks "are you sure?" and then for the PIN.
6. **Check the photos are saved:** in the AWS console, go to **S3**, then open the bucket named under **PhotoBucketName** in the stack's Outputs. After a few captures, you should see today's folder, for example `20261109/`. Inside it, you should see `unknown/`, and after pressing Yes or No, `success/` or `failure/`.
7. **Monday's rehearsal:** the students time how long each prediction takes on the tablet, so they can write it in their report.

## Each day

**Start or stop the server:** go to **EC2**, then **Instances**, then **signlang-server**, then **Instance state**, then **Start** or **Stop**. After **Start**, wait about 2 minutes before the page works. The address and the statistics stay the same.

| Day | What to do |
|---|---|
| Mon 9 | Start it in the morning, rehearse, then reset the statistics |
| Tue 10 (fair) | Running from Monday. **Stop** it after school. |
| Wed 11 (fair) | **Start** it **30–45 minutes before school**, check it on the tablet, then at the end do "Finishing on 11 November" below |

**Idle safety net:** if the server is unused for 3 hours, for example overnight, it stops by itself and you get an email. Just start it again.

## If the server won't start ("insufficient capacity")

1. Wait 2–3 minutes and click **Start** again.
2. If it still fails, change the server size while it's stopped. Go to **Actions**, then **Instance settings**, then **Change instance type**, and choose `c6i.2xlarge` (or `m7i.2xlarge`, or `c7i.xlarge`). Then click **Start**. The address and statistics stay the same.
3. Meanwhile, use the laptop with `start.bat`.

## If something else goes wrong

| Problem | Fix |
|---|---|
| `upload.bat` can't connect | Your home IP may have changed. Go to **EC2**, then **Security Groups**, then **signlang-firewall**, then **Edit inbound rules**. On the port 22 rule choose **My IP**, then click **Save**. |
| The page doesn't load, or there's a certificate error | Check that DuckDNS shows the FixedIpAddress (step 4), then wait a minute. |
| No photos appear in S3 | Run `sudo journalctl -u signlang -n 50` on the server (see the next row) and look for "Could not save a photo to S3". The app itself keeps working. |
| You need to see the server's messages | In a command prompt in the project folder, run `ssh -i deploy\signlang-key.pem ubuntu@mysignlang.duckdns.org`. Then run `sudo journalctl -u signlang -n 50` for the app, or `sudo journalctl -u caddy -n 50` for https and the login. |

## Finishing on 11 November

1. **Save the numbers first:** double-click `deploy\download_stats.bat`, then type the login. The numbers are saved in `stats-from-aws.json` in the project folder.
2. **Save the photos:**
   1. Open **CloudShell** (the `>_` icon) and type the following, with your **PhotoBucketName** from the stack's Outputs in place of `BUCKET`:

      ```bash
      aws s3 sync s3://BUCKET photos
      zip -r photos.zip photos
      ```

   2. Click **Actions**, then **Download file**, and type `photos.zip`. Unzip it on the laptop. It has one folder per day (for example `20261110`), each with `success`, `failure` and `unknown` inside.
3. **Empty the bucket.** AWS will not delete a bucket that still has photos in it. In CloudShell:

   ```bash
   aws s3 rm s3://BUCKET --recursive
   ```

4. Go to **CloudFormation**, then **signlang**, then **Delete**. Wait until it's gone. This removes the server, disk, IP address, firewall, key, photo bucket, permission, alarm, email topic and budget. If it says the bucket could not be deleted, do step 3 again, then click **Delete** again.
5. To check nothing is left: go to **Resource Groups & Tag Editor**, then **Tag Editor**. Set Region to Mumbai, Resource types to All, and Tag key `Project` with value `sign_project`. Click **Search**, and it should find nothing.
6. Delete `deploy\signlang-key.pem` from the laptop. You can also delete the `mysignlang` name on duckdns.org.
7. Check **Billing** over the next few days to make sure the charges have stopped.
