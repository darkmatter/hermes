# Forms & inputs

Source: `components/ui/{form,input,textarea,select,checkbox,radio-group,switch,slider,label,input-otp}.tsx`. Forms use `react-hook-form` + `zod` (both installed) with the `Form` wrapper.

## Primitives

```tsx
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Select, SelectTrigger, SelectValue, SelectContent, SelectItem,
} from "@/components/ui/select"
```

Always pair a control with a `Label` (wired via `htmlFor`/`id`):

```tsx
<div className="grid gap-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="you@darkmatter.io" />
</div>

<Select>
  <SelectTrigger><SelectValue placeholder="Pick a product" /></SelectTrigger>
  <SelectContent>
    <SelectItem value="protocols">Protocols</SelectItem>
    <SelectItem value="trading">Trading</SelectItem>
  </SelectContent>
</Select>
```

Field borders use the `input` token and focus rings use `ring` — don't override with raw colors.

## Form (react-hook-form + zod)

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({ email: z.string().email() })

function SignupForm() {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  })
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit((v) => console.log(v))} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl><Input placeholder="you@darkmatter.io" {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Join</Button>
      </form>
    </Form>
  )
}
```

`FormMessage` renders zod validation errors in the `destructive` color automatically.

## Accessibility

- Every input needs an associated `Label` / `FormLabel`.
- Keep `FormMessage` present so errors are announced.
- `Switch`, `Checkbox`, `RadioGroupItem` need labels too.

## Common mistakes

- Placeholder-only fields with no `Label`.
- Building custom validation instead of zod + `FormMessage`.
- Overriding `border-input` / `ring` with raw colors.

## Never invent

Use the exact subcomponent names above (`SelectTrigger`, `SelectContent`, `SelectItem`, `FormField`, `FormItem`, …). No extra props beyond what the source exports.
