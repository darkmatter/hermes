# Message Composition with MML (MIME Meta Language)

Himalaya uses MML for composing emails. MML is a simple XML-based syntax that compiles to MIME messages.

## Basic Message Structure

```
From: sender@example.com
To: recipient@example.com
Subject: Hello World

This is the message body.
```

## Headers

Common headers: `From`, `To`, `Cc`, `Bcc`, `Subject`, `Reply-To`, `In-Reply-To`.

### Address Formats

```
To: user@example.com
To: John Doe <john@example.com>
To: user1@example.com, user2@example.com
```

## MML for Rich Emails

### Multipart (alternative text/html)

```
From: alice@localhost
To: bob@localhost
Subject: Multipart Example

<#multipart type=alternative>
This is the plain text version.
<#part type=text/html>
<html><body><h1>This is the HTML version</h1></body></html>
<#/multipart>
```

### Attachments

```
<#part filename=/path/to/document.pdf><#/part>
<#part filename=/path/to/file.pdf name=report.pdf><#/part>
```

### Inline Images

```
<#multipart type=related>
<#part type=text/html>
<html><body><img src="cid:image1"></body></html>
<#part disposition=inline id=image1 filename=/path/to/image.png><#/part>
<#/multipart>
```

### Mixed Content (Text + Attachments)

```
<#multipart type=mixed>
<#part type=text/plain>
Please find the attached files.
<#part filename=/path/to/file1.pdf><#/part>
<#part filename=/path/to/file2.zip><#/part>
<#/multipart>
```

## MML Tag Reference

### `<#multipart>`

- `type=alternative`: Different representations of same content
- `type=mixed`: Independent parts (text + attachments)
- `type=related`: Parts that reference each other (HTML + images)

### `<#part>`

- `type=<mime-type>`: Content type
- `filename=<path>`: File to attach
- `name=<name>`: Display name for attachment
- `disposition=inline`: Display inline
- `id=<cid>`: Content ID for referencing in HTML

## Composing from CLI

### Send from stdin (use this from Hermes)

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF
```

### Prefill headers from CLI

```bash
himalaya message write \
  -H "To:recipient@example.com" \
  -H "Subject:Quick Message" \
  "Message body here"
```
