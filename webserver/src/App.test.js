import React from 'react';
import { render } from '@testing-library/react';
import Gallery from './Gallery';

test('renders learn react link', () => {
  const { getByText } = render(<Gallery />);
  const linkElement = getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
