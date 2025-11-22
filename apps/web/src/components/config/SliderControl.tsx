"use client"

import { Slider } from "@/components/ui/slider"

interface SliderControlProps {
    label: string
    value: number
    onChange: (value: number) => void
    min: number
    max: number
    step: number
    info?: string
    unit?: string
}

export function SliderControl({
    label,
    value,
    onChange,
    min,
    max,
    step,
    info,
    unit = ""
}: SliderControlProps) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-black">{label}</label>
                <span className="text-sm text-gray-600">
                    {value}{unit}
                </span>
            </div>
            <Slider
                value={[value]}
                onValueChange={(values) => onChange(values[0])}
                min={min}
                max={max}
                step={step}
                className="w-full"
            />
            {info && <p className="text-xs text-gray-600">{info}</p>}
        </div>
    )
}
