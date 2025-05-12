import React from 'react';
import { render, screen } from '@testing-library/react'
import NotFound from '../NotFound';

test("Not Found renders successfully", () => {
    render(<NotFound/>);

    const element = screen.getByText(/404: Not Found/i);

    expect(element).toBeInTheDocument();
})