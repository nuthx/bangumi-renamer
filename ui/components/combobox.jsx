import {
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  Combobox as HeadlessCombobox,
} from "@headlessui/react"
import { CaretDownIcon, PlusIcon, XIcon } from "@phosphor-icons/react"
import { useState } from "react"

import { cn } from "@/utils/cn"

export function Combobox({ options, value, onChange, onOptionsChange, placeholder, className }) {
  const [query, setQuery] = useState("")

  const filteredOptions = query ? options.filter((opt) => opt.toLowerCase().includes(query.toLowerCase())) : options

  const handleChange = async (selected) => {
    const newValue = selected ?? query
    await onChange(newValue)
    if (!selected && query) await onOptionsChange?.([...options, query])
  }

  return (
    <HeadlessCombobox value={value} onChange={handleChange} onClose={() => setQuery("")}>
      <div className={cn("relative", className)}>
        <ComboboxInput
          className={cn(
            "w-full h-8 px-3 pr-8 text-primary placeholder:text-muted truncate rounded-sm transition",
            "bg-background hover:bg-background-dark/50 border border-b-muted",
            "focus:bg-background-dark/50 focus:border-muted",
          )}
          displayValue={() => value}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
        />
        <ComboboxButton className="absolute inset-y-0 right-0 flex-center px-3 cursor-pointer">
          <CaretDownIcon className="size-4 text-secondary shrink-0 transition-all group-data-open:rotate-180" />
        </ComboboxButton>
      </div>

      <ComboboxOptions
        anchor="bottom"
        className="w-(--input-width) mt-1 p-1 space-y-1 border bg-background/80 backdrop-blur-sm shadow-lg/10 rounded-md transition data-closed:-translate-y-2 data-closed:opacity-0"
        transition
      >
        <ComboboxOption
          value=""
          className={cn(
            "group relative flex items-center h-8 px-3 rounded-sm cursor-pointer transition",
            "hover:bg-background-dark data-selected:bg-background-dark",
          )}
        >
          <span className="cursor-pointer">{placeholder}</span>
          <div className="absolute left-0 w-0.75 h-3.5 rounded-full bg-accent group-data-selected:block hidden" />
        </ComboboxOption>
        {filteredOptions.map((item) => (
          <ComboboxOption
            key={item}
            value={item}
            className={cn(
              "group relative flex items-center justify-between gap-2 min-h-8 py-1 pl-3 pr-8 rounded-sm cursor-pointer transition",
              "hover:bg-background-dark data-selected:bg-background-dark",
            )}
          >
            <span className="break-all cursor-pointer">{item}</span>
            <div className="absolute left-0 w-0.75 h-3.5 rounded-full bg-accent group-data-selected:block hidden" />
            {onOptionsChange && item !== value && (
              <button
                type="button"
                onPointerDown={(e) => e.preventDefault()}
                onClick={() => onOptionsChange(options.filter((opt) => opt !== item))}
                className="absolute right-1 opacity-0 group-hover:opacity-100 p-1 rounded-sm cursor-pointer hover:bg-muted/40 text-secondary hover:text-primary transition"
              >
                <XIcon className="size-4" />
              </button>
            )}
          </ComboboxOption>
        ))}
        {query && !options.includes(query) && (
          <ComboboxOption
            value={null}
            className={cn(
              "flex items-center gap-2 min-h-8 py-1.5 px-3 text-accent rounded-sm cursor-pointer transition",
              "hover:bg-background-dark data-selected:bg-background-dark",
            )}
          >
            <PlusIcon className="size-4 shrink-0" />
            <span className="break-all cursor-pointer">新增 {query}</span>
          </ComboboxOption>
        )}
      </ComboboxOptions>
    </HeadlessCombobox>
  )
}
