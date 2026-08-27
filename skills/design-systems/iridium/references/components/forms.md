# Forms & Inputs

## Input & Label
`import { Input } from "@native/ui/input"` (extends native `<input>` props — `type`, `placeholder`, etc.). `import { Label } from "@native/ui/label"` (Radix Label). Source: `packages/ui/src/input.tsx`, `label.tsx`.

```tsx
import { Input } from "@native/ui/input"
import { Label } from "@native/ui/label"

<div className="grid gap-2">
  <Label htmlFor="amount">Amount</Label>
  <Input id="amount" type="number" inputMode="decimal" placeholder="0.00" className="tabular-nums" />
</div>
```
Add `tabular-nums` on numeric inputs so digits align with the rest of the UI.

## Select
`import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem, SelectGroup, SelectLabel, SelectSeparator } from "@native/ui/select"`. Radix Select. Source: `packages/ui/src/select.tsx`.

```tsx
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@native/ui/select"

<Select defaultValue="usdc">
  <SelectTrigger className="w-40"><SelectValue placeholder="Token" /></SelectTrigger>
  <SelectContent>
    <SelectItem value="usdc">USDC</SelectItem>
    <SelectItem value="weth">WETH</SelectItem>
  </SelectContent>
</Select>
```

## Checkbox & RadioGroup
`import { Checkbox } from "@native/ui/checkbox"`, `import { RadioGroup, RadioGroupItem } from "@native/ui/radio-group"`. Radix-based. Pair each with a `Label`.

```tsx
<div className="flex items-center gap-2">
  <Checkbox id="reduce" /><Label htmlFor="reduce">Reduce-only</Label>
</div>

<RadioGroup defaultValue="market">
  <div className="flex items-center gap-2"><RadioGroupItem value="market" id="m" /><Label htmlFor="m">Market</Label></div>
  <div className="flex items-center gap-2"><RadioGroupItem value="limit" id="l" /><Label htmlFor="l">Limit</Label></div>
</RadioGroup>
```

## InputOTP
`import { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator } from "@native/ui/input-otp"`. For verification codes.

## Field vs Form — which to use
Two composition systems exist; pick one per form, don't mix within a field.

- **Field** (`@native/ui/field`): presentational form scaffolding, no form library required. Exports `Field, FieldLabel, FieldDescription, FieldError, FieldGroup, FieldLegend, FieldSeparator, FieldSet, FieldContent, FieldTitle`. Use for simple/controlled forms and settings panels.
  ```tsx
  import { Field, FieldLabel, FieldDescription, FieldError } from "@native/ui/field"
  import { Input } from "@native/ui/input"

  <Field>
    <FieldLabel htmlFor="slip">Max slippage</FieldLabel>
    <Input id="slip" defaultValue="0.5" className="tabular-nums" />
    <FieldDescription>Percent tolerance before the order reverts.</FieldDescription>
    <FieldError>Must be between 0 and 5.</FieldError>
  </Field>
  ```

- **Form** (`@native/ui/form`): the react-hook-form binding (shadcn pattern). Exports `Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage, useFormField`. Use with `react-hook-form` (+ a resolver) for validated forms.
  ```tsx
  "use client"
  import { useForm } from "react-hook-form"
  import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@native/ui/form"
  import { Input } from "@native/ui/input"

  const form = useForm({ defaultValues: { amount: "" } })
  <Form {...form}>
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <FormField control={form.control} name="amount" render={({ field }) => (
        <FormItem>
          <FormLabel>Amount</FormLabel>
          <FormControl><Input {...field} className="tabular-nums" /></FormControl>
          <FormMessage />
        </FormItem>
      )} />
    </form>
  </Form>
  ```

## PillToggle & PillFilter
`import { PillToggle, PillFilter } from "@native/ui/pill-toggle"`. Compact segmented controls with amber active state.
- `PillToggle<T>`: single-select. Props `options: {label,value}[]`, `value`, `onChange`, `mono?`.
- `PillFilter`: multi-select. Props `options: {key,label}[]`, `active: Set<string>`, `onToggle`.

```tsx
<PillToggle options={[{label:"1H",value:"1h"},{label:"1D",value:"1d"}]} value={tf} onChange={setTf} />
```

## Common mistakes / never invent
- Don't mix `Field*` and `Form*` for the same control. `Form*` requires a `react-hook-form` context.
- Always associate labels (`htmlFor`/`id`) for accessibility.
- Numeric inputs get `tabular-nums`.
- Don't invent input variants or sizes; `Input` is a styled native input.
