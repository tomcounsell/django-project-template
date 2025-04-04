# Tailwind v4 Migration Checklist

This document provides a step-by-step process for migrating from Tailwind CSS v3 to v4 across an entire codebase of HTML files.

## Preparation

1. Create a backup of your codebase
2. Run tests to establish baseline functionality
3. Document current appearance with screenshots for key interfaces

## Search and Replace Process

### 1. Renamed Utilities

#### Shadow Scale
- [ ] Replace `shadow-sm` → `shadow-xs`
- [ ] Replace `shadow` → `shadow-sm`
- [ ] Replace `drop-shadow-sm` → `drop-shadow-xs`
- [ ] Replace `drop-shadow` → `drop-shadow-sm`

#### Blur Scale
- [ ] Replace `blur-sm` → `blur-xs`
- [ ] Replace `blur` → `blur-sm`
- [ ] Replace `backdrop-blur-sm` → `backdrop-blur-xs`
- [ ] Replace `backdrop-blur` → `backdrop-blur-sm`

#### Rounded Scale
- [ ] Replace `rounded-sm` → `rounded-xs`
- [ ] Replace `rounded` → `rounded-sm`

#### Outline Utilities
- [ ] Replace `outline-none` → `outline-hidden`
- [ ] Replace `*:outline-none` → `*:outline-hidden`
- [ ] Replace any instances of `outline outline-2` → `outline-2`

#### Ring Utilities
- [ ] Replace `ring` → `ring-3` (default ring width changed from 3px to 1px)
- [ ] Add `ring-blue-500` to any `ring` or `ring-3` that doesn't specify a color

### 2. Removed Deprecated Utilities

#### Opacity Utilities
- [ ] Replace `bg-opacity-{value}` → `bg-{color}/{value}`
- [ ] Replace `text-opacity-{value}` → `text-{color}/{value}`
- [ ] Replace `border-opacity-{value}` → `border-{color}/{value}`
- [ ] Replace `divide-opacity-{value}` → `divide-{color}/{value}`
- [ ] Replace `ring-opacity-{value}` → `ring-{color}/{value}`
- [ ] Replace `placeholder-opacity-{value}` → `placeholder-{color}/{value}`

#### Flex Utilities
- [ ] Replace `flex-shrink-{value}` → `shrink-{value}`
- [ ] Replace `flex-grow-{value}` → `grow-{value}`

#### Other Deprecated Utilities
- [ ] Replace `overflow-ellipsis` → `text-ellipsis`
- [ ] Replace `decoration-slice` → `box-decoration-slice`
- [ ] Replace `decoration-clone` → `box-decoration-clone`

### 3. Border Color Defaults
- [ ] Add explicit color (e.g., `border-gray-200`) to all `border` utilities that don't specify a color
- [ ] Add explicit color (e.g., `divide-gray-200`) to all `divide-x` and `divide-y` utilities that don't specify a color

### 4. Space Utility Changes
- [ ] Consider replacing `space-x-*` and `space-y-*` with `flex flex-col` or `flex flex-row` and `gap-*` utilities
- [ ] Audit pages for unexpected spacing changes where `space-y-*` or `space-x-*` are used

### 5. Gradient Handling in Variants
- [ ] Audit gradient utilities with variants to ensure proper rendering
- [ ] Add `via-none` when trying to unset a middle color stop in a gradient with variants

### 6. Variant Stacking Order
- [ ] Reverse the order of stacked variants (now applied left to right instead of right to left)
- [ ] Example: Change `first:*:pt-0` → `*:first:pt-0`
- [ ] Example: Change `last:*:pb-0` → `*:last:pb-0`
- [ ] Pay special attention to combinations with direct child variant (`*`) and typography plugin variants

### 7. CSS Variables in Arbitrary Values
- [ ] Replace `bg-[--variable-name]` → `bg-(--variable-name)`
- [ ] Replace `text-[--variable-name]` → `text-(--variable-name)`
- [ ] Replace all other instances of `*-[--*]` with `*-(--*)`

### 8. Hover Handling
- [ ] Audit mobile functionality where hover effects are critical for operation
- [ ] Consider adding explicit focus/active states for touch devices

### 9. Transition Properties
- [ ] Check outline transitions that may now animate color unexpectedly
- [ ] Add explicit outline colors to both states where transitions are used

## Testing & Validation

1. Test pages on multiple devices (desktop, tablet, mobile)
2. Verify hover interactions work as expected on touch devices
3. Check shadow, border, and outline rendering
4. Validate form element styling (especially with outline-hidden)
5. Test dark mode if applicable
6. Verify gradients with variants render correctly

## Additional Configuration

1. Update any custom container configurations
2. Consider adding baseline CSS if needed to maintain v3 behaviors:
   ```css
   /* For default border colors */
   @layer base {
     *,
     ::after,
     ::before,
     ::backdrop,
     ::file-selector-button {
       border-color: var(--color-gray-200, currentColor);
     }
   }
   
   /* For placeholder text color */
   @layer base {
     input::placeholder,
     textarea::placeholder {
       color: var(--color-gray-400);
     }
   }
   
   /* For pointer cursor on buttons */
   @layer base {
     button:not(:disabled),
     [role="button"]:not(:disabled) {
       cursor: pointer;
     }
   }
   ```

## Final Steps

1. Update any documentation references to Tailwind utilities
2. Inform team of key changes, especially around default behaviors
3. Update test snapshots or visual regression tests as needed